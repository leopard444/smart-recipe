from datetime import datetime
from app.extensions import db

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    images = db.Column(db.JSON, default=list)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=True)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum('published', 'hidden', 'deleted', name='post_status_enum'), default='published')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic',
                               cascade='all, delete-orphan', order_by='Comment.created_at.asc()')
    likes = db.relationship('Like', backref='post', lazy='dynamic',
                            cascade='all, delete-orphan')

    def to_dict(self, current_user_id=None) -> dict:
        is_liked = False
        if current_user_id:
            is_liked = Like.query.filter_by(post_id=self.id, user_id=current_user_id).first() is not None

        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.author.username if self.author else 'Unknown',
            'user_avatar': self.author.avatar_url if self.author else None,
            'title': self.title,
            'content': self.content,
            'images': self.images or [],
            'recipe_id': self.recipe_id,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'is_pinned': self.is_pinned,
            'is_liked': is_liked,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # For nested comments
    parent = db.relationship('Comment', remote_side=[id], backref='replies')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'username': self.author.username if self.author else 'Unknown',
            'user_avatar': self.author.avatar_url if self.author else None,
            'parent_id': self.parent_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'replies': [r.to_dict() for r in self.replies] if self.replies else [],
        }


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),
    )
