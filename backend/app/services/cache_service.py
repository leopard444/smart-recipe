import json
from typing import Optional
from redis import Redis

class CacheService:
    PREFIX_RECIPE = "recipe:"
    PREFIX_SESSION = "session:"
    PREFIX_RATE_LIMIT = "ratelimit:"
    PREFIX_VIEW = "views:"

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    # --- Recipe cache ---
    def get_recipe(self, prompt_hash: str) -> Optional[list]:
        if not self.redis:
            return None
        data = self.redis.get(f"{self.PREFIX_RECIPE}{prompt_hash}")
        return json.loads(data) if data else None

    def set_recipe(self, prompt_hash: str, recipes: list, ttl: int = 86400):
        if not self.redis:
            return
        key = f"{self.PREFIX_RECIPE}{prompt_hash}"
        self.redis.setex(key, ttl, json.dumps(recipes, ensure_ascii=False))

    # --- Rate limiting ---
    def check_rate_limit(self, identifier: str, action: str, max_req: int, window: int = 60) -> bool:
        """Returns True if within limit, False if exceeded."""
        if not self.redis:
            return True
        key = f"{self.PREFIX_RATE_LIMIT}{action}:{identifier}"
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, window)
        return current <= max_req

    def get_rate_limit_remaining(self, identifier: str, action: str, max_req: int) -> int:
        if not self.redis:
            return max_req
        key = f"{self.PREFIX_RATE_LIMIT}{action}:{identifier}"
        val = self.redis.get(key)
        return max(min(max_req - int(val or 0), max_req), 0)

    # --- View counting ---
    def increment_view(self, recipe_id: int):
        if not self.redis:
            return
        self.redis.zincrby(f"{self.PREFIX_VIEW}recipes", 1, str(recipe_id))

    def get_top_viewed(self, limit: int = 10) -> list[int]:
        if not self.redis:
            return []
        results = self.redis.zrevrange(f"{self.PREFIX_VIEW}recipes", 0, limit - 1)
        return [int(r) for r in results]

    # --- Session blacklist ---
    def blacklist_token(self, jti: str, ttl: int):
        if not self.redis:
            return
        self.redis.setex(f"{self.PREFIX_SESSION}bl:{jti}", ttl, "1")

    def is_blacklisted(self, jti: str) -> bool:
        if not self.redis:
            return False
        return self.redis.exists(f"{self.PREFIX_SESSION}bl:{jti}") > 0
