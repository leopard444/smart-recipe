from datetime import datetime
from app.extensions import db
import bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    role = db.Column(db.Enum('user', 'admin', name='user_role'), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'), self.password_hash.encode('utf-8')
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.username}>'
