"""Admin API endpoints."""
from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.user import User
from app.models.recipe import Recipe
from app.models.community import Post
from app.models.admin import Category, AdminLog
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def dashboard_stats():
    stats = {
        'total_users': User.query.count(),
        'total_recipes': Recipe.query.filter(Recipe.status != 'deleted').count(),
        'total_posts': Post.query.filter(Post.status != 'deleted').count(),
        'total_comments': 0,  # Simplified; can add Comment.query.count()
        'pending_recipes': Recipe.query.filter(Recipe.status == 'published').count(),
        'flagged_posts': Post.query.filter(Post.status == 'hidden').count(),
    }
    return jsonify({'code': 200, 'data': stats}), 200


# --- Recipe Moderation ---

@admin_bp.route('/recipes/pending', methods=['GET'])
@admin_required
def pending_recipes():
    page = request.args.get('page', 1, type=int)
    query = Recipe.query.filter(Recipe.status.in_(['published', 'hidden']))\
        .order_by(Recipe.created_at.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    return jsonify({
        'code': 200,
        'data': {
            'items': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'perPage': pagination.per_page,
            'pages': pagination.pages,
        }
    }), 200


@admin_bp.route('/recipes/<int:id>/status', methods=['PUT'])
@admin_required
def update_recipe_status(id: int):
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({'code': 404, 'message': '食谱不存在'}), 404

    data = request.get_json()
    status = data.get('status', 'published')
    if status not in ('published', 'hidden', 'deleted'):
        return jsonify({'code': 400, 'message': '无效状态'}), 400

    recipe.status = status
    db.session.add(AdminLog(
        admin_id=g.user_id,
        action=f'recipe_{status}',
        target_type='recipe',
        target_id=id,
        detail=f'Set recipe "{recipe.title}" to {status}',
    ))
    db.session.commit()
    return jsonify({'code': 200, 'message': f'食谱已{status}'}), 200


@admin_bp.route('/recipes/featured', methods=['POST'])
@admin_required
def set_featured_recipes():
    """Set featured recipe IDs."""
    data = request.get_json()
    recipe_ids = data.get('recipe_ids', [])
    # Store featured recipe IDs in a system config or Redis
    from app.extensions import get_redis
    redis = get_redis()
    if redis:
        import json
        redis.set('admin:featured_recipes', json.dumps(recipe_ids))
    return jsonify({'code': 200, 'message': '热门食谱已更新'}), 200


# --- Category Management ---

@admin_bp.route('/categories', methods=['GET'])
@admin_required
def list_categories():
    categories = Category.query.order_by(Category.sort_order).all()
    return jsonify({'code': 200, 'data': [c.to_dict() for c in categories]}), 200


@admin_bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'code': 400, 'message': '分类名称不能为空'}), 400

    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'code': 409, 'message': '分类名称已存在'}), 409

    cat = Category(
        name=data['name'],
        description=data.get('description', ''),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({'code': 200, 'data': cat.to_dict()}), 201


@admin_bp.route('/categories/<int:id>', methods=['PUT'])
@admin_required
def update_category(id: int):
    cat = Category.query.get(id)
    if not cat:
        return jsonify({'code': 404, 'message': '分类不存在'}), 404

    data = request.get_json()
    if 'name' in data:
        existing = Category.query.filter(Category.name == data['name'], Category.id != id).first()
        if existing:
            return jsonify({'code': 409, 'message': '分类名称已存在'}), 409
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'sort_order' in data:
        cat.sort_order = data['sort_order']

    db.session.commit()
    return jsonify({'code': 200, 'data': cat.to_dict()}), 200


@admin_bp.route('/categories/<int:id>', methods=['DELETE'])
@admin_required
def delete_category(id: int):
    cat = Category.query.get(id)
    if not cat:
        return jsonify({'code': 404, 'message': '分类不存在'}), 404
    # Unlink recipes from this category
    Recipe.query.filter_by(category_id=id).update({'category_id': None})
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'code': 200, 'message': '已删除'}), 200


# --- User Management ---

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    query = User.query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    return jsonify({
        'code': 200,
        'data': {
            'items': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'perPage': pagination.per_page,
            'pages': pagination.pages,
        }
    }), 200


@admin_bp.route('/users/<int:id>/status', methods=['PUT'])
@admin_required
def update_user_status(id: int):
    user = User.query.get(id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()
    user.is_active = data.get('is_active', True)
    db.session.add(AdminLog(
        admin_id=g.user_id,
        action='user_status',
        target_type='user',
        target_id=id,
        detail=f"{'Enable' if user.is_active else 'Disable'} user {user.username}",
    ))
    db.session.commit()
    return jsonify({'code': 200, 'message': '用户状态已更新'}), 200
