"""Robust JSON parser for LLM recipe responses with multiple fallback strategies."""
import json
import re
import logging

logger = logging.getLogger(__name__)


def parse_recipe_response(content: str) -> list | None:
    """
    Parse LLM JSON response with multiple fallback strategies.
    Returns list of recipe dicts or None if all strategies fail.
    """
    if not content or not content.strip():
        return None

    # Strategy 1: Direct JSON.parse
    try:
        data = json.loads(content)
        return _extract_recipes(data)
    except (json.JSONDecodeError, TypeError):
        pass

    # Strategy 2: Extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            return _extract_recipes(data)
        except (json.JSONDecodeError, TypeError):
            pass

    # Strategy 3: Find the outermost {...} block
    # Find first { and matching }
    depth = 0
    start = -1
    for i, ch in enumerate(content):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start >= 0:
                json_str = content[start:i + 1]
                try:
                    data = json.loads(json_str)
                    return _extract_recipes(data)
                except (json.JSONDecodeError, TypeError):
                    pass
                break

    # Strategy 4: Try to fix common JSON issues and retry
    try:
        cleaned = content.strip()
        # Remove trailing commas before } or ]
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
        # Fix unquoted keys (simple cases)
        data = json.loads(cleaned)
        return _extract_recipes(data)
    except (json.JSONDecodeError, TypeError):
        pass

    logger.warning(f"Failed to parse LLM response: {content[:500]}...")
    return None


def _extract_recipes(data: dict) -> list:
    """Extract and validate recipe list from parsed JSON."""
    if not isinstance(data, dict):
        return None

    # Direct recipes array
    recipes = data.get('recipes', [])
    if isinstance(recipes, list) and recipes:
        return [_validate_recipe(r) for r in recipes if isinstance(r, dict)]

    # Top-level might be a single recipe
    if data.get('title'):
        return [_validate_recipe(data)]

    return None


def _validate_recipe(r: dict) -> dict:
    """Fill in missing fields with sensible defaults."""
    return {
        'id': r.get('id', ''),
        'title': r.get('title', '未命名食谱'),
        'description': r.get('description', ''),
        'cookingTime': r.get('cookingTime', r.get('cooking_time', '30分钟')),
        'prepTime': r.get('prepTime', r.get('prep_time', '10分钟')),
        'difficulty': r.get('difficulty', '中等'),
        'dietType': r.get('dietType', r.get('diet_type', '家常')),
        'tags': r.get('tags', []),
        'servings': int(r.get('servings', 2)),
        'ingredients': [
            {
                'name': i.get('name', ''),
                'amount': i.get('amount', '适量'),
                'notes': i.get('notes', ''),
            }
            for i in r.get('ingredients', [])
            if i.get('name')
        ],
        'steps': [
            {
                'stepNumber': s.get('stepNumber', s.get('step_number', idx + 1)),
                'instruction': s.get('instruction', ''),
            }
            for idx, s in enumerate(r.get('steps', []))
            if s.get('instruction')
        ],
        'nutrition': {
            'calories': r.get('nutrition', {}).get('calories', '--'),
            'protein': r.get('nutrition', {}).get('protein', '--'),
            'carbs': r.get('nutrition', {}).get('carbs', '--'),
            'fat': r.get('nutrition', {}).get('fat', '--'),
            'fiber': r.get('nutrition', {}).get('fiber', '--'),
        },
        'tips': r.get('tips', ''),
        'imageSuggestion': r.get('imageSuggestion', r.get('image_suggestion', '')),
    }
