"""Community API endpoints."""
from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.community import Post, Comment, Like
from app.utils.decorators import login_required, optional_auth

community_bp = Blueprint('community', __name__)


def _paginate(query, page: int = 1, per_page: int = 10):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    current_user_id = getattr(g, 'user_id', None)
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'perPage': pagination.per_page,
        'pages': pagination.pages,
    }


@community_bp.route('/posts', methods=['GET'])
@optional_auth
def list_posts():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    sort = request.args.get('sort', 'newest')

    query = Post.query.filter(Post.status == 'published')

    if keyword:
        query = query.filter(
            db.or_(
                Post.title.ilike(f'%{keyword}%'),
                Post.content.ilike(f'%{keyword}%'),
            )
        )

    if sort == 'popular':
        query = query.order_by(Post.like_count.desc(), Post.created_at.desc())
    elif sort == 'pinned':
        query = query.order_by(Post.is_pinned.desc(), Post.created_at.desc())
    else:
        query = query.order_by(Post.is_pinned.desc(), Post.created_at.desc())

    result = _paginate(query, page)

    # Mark is_liked for each post
    user_id = getattr(g, 'user_id', None)
    if user_id:
        post_ids = [p['id'] for p in result['items']]
        liked_ids = set(
            l.post_id for l in Like.query.filter(
                Like.user_id == user_id, Like.post_id.in_(post_ids)
            ).all()
        )
        for p in result['items']:
            p['is_liked'] = p['id'] in liked_ids

    return jsonify({'code': 200, 'data': result}), 200


@community_bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title or not content:
        return jsonify({'code': 400, 'message': '标题和内容不能为空'}), 400

    post = Post(
        user_id=g.user_id,
        title=title,
        content=content,
        images=data.get('images', []),
        recipe_id=data.get('recipe_id'),
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'code': 200, 'data': post.to_dict()}), 201


@community_bp.route('/posts/<int:id>', methods=['GET'])
@optional_auth
def get_post(id: int):
    post = Post.query.get(id)
    if not post or post.status == 'deleted':
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    post.view_count += 1
    db.session.commit()

    return jsonify({'code': 200, 'data': post.to_dict()}), 200


@community_bp.route('/posts/<int:id>', methods=['PUT'])
@login_required
def update_post(id: int):
    post = Post.query.get(id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404
    if post.user_id != g.user_id:
        return jsonify({'code': 403, 'message': '无权修改此帖子'}), 403

    data = request.get_json()
    if 'title' in data: post.title = data['title']
    if 'content' in data: post.content = data['content']
    if 'images' in data: post.images = data['images']
    if 'status' in data: post.status = data['status']

    db.session.commit()
    return jsonify({'code': 200, 'data': post.to_dict()}), 200


@community_bp.route('/posts/<int:id>', methods=['DELETE'])
@login_required
def delete_post(id: int):
    post = Post.query.get(id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404
    if post.user_id != g.user_id:
        return jsonify({'code': 403, 'message': '无权删除此帖子'}), 403

    post.status = 'deleted'
    db.session.commit()
    return jsonify({'code': 200, 'message': '已删除'}), 200


@community_bp.route('/posts/<int:id>/like', methods=['POST'])
@login_required
def toggle_like(id: int):
    post = Post.query.get(id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    existing = Like.query.filter_by(user_id=g.user_id, post_id=id).first()
    if existing:
        db.session.delete(existing)
        post.like_count = max((post.like_count or 1) - 1, 0)
        db.session.commit()
        return jsonify({'code': 200, 'data': {'liked': False}}), 200
    else:
        db.session.add(Like(user_id=g.user_id, post_id=id))
        post.like_count = (post.like_count or 0) + 1
        db.session.commit()
        return jsonify({'code': 200, 'data': {'liked': True}}), 200


@community_bp.route('/posts/<int:id>/comments', methods=['GET'])
@optional_auth
def get_comments(id: int):
    comments = Comment.query.filter_by(post_id=id, parent_id=None)\
        .order_by(Comment.created_at.asc()).all()
    return jsonify({'code': 200, 'data': [c.to_dict() for c in comments]}), 200


@community_bp.route('/posts/<int:id>/comments', methods=['POST'])
@login_required
def create_comment(id: int):
    post = Post.query.get(id)
    if not post:
        return jsonify({'code': 404, 'message': '帖子不存在'}), 404

    data = request.get_json()
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')

    if not content:
        return jsonify({'code': 400, 'message': '评论内容不能为空'}), 400

    comment = Comment(
        post_id=id,
        user_id=g.user_id,
        parent_id=parent_id,
        content=content,
    )
    db.session.add(comment)
    post.comment_count = (post.comment_count or 0) + 1
    db.session.commit()
    return jsonify({'code': 200, 'data': comment.to_dict()}), 201


@community_bp.route('/comments/<int:id>', methods=['DELETE'])
@login_required
def delete_comment(id: int):
    comment = Comment.query.get(id)
    if not comment:
        return jsonify({'code': 404, 'message': '评论不存在'}), 404
    if comment.user_id != g.user_id:
        return jsonify({'code': 403, 'message': '无权删除此评论'}), 403

    post = comment.post
    if post:
        post.comment_count = max((post.comment_count or 1) - 1, 0)
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'code': 200, 'message': '已删除'}), 200
