from datetime import datetime
from app.extensions import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), default='')
    sort_order = db.Column(db.Integer, default=0)

    # Relationships
    recipes = db.relationship('Recipe', backref='category', lazy='dynamic')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sort_order': self.sort_order,
            'sortOrder': self.sort_order,
        }


class AdminLog(db.Model):
    __tablename__ = 'admin_logs'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=True)
    detail = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship('User', backref='admin_logs')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_name': self.admin.username if self.admin else 'Unknown',
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'detail': self.detail,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
