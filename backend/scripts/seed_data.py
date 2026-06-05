#!/usr/bin/env python3
"""Seed the database with initial data."""
import sys
sys.path.insert(0, '.')

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.admin import Category

app = create_app('development')

def seed():
    with app.app_context():
        db.create_all()

        # Create admin user
        admin = User.query.filter_by(email='admin@recipe.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@recipe.com',
                role='admin',
                is_active=True,
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print('Created admin user: admin@recipe.com / admin123')

        # Create default categories
        categories = ['早餐', '午餐', '晚餐', '快手菜', '汤羹', '主食', '小食', '饮品']
        for i, name in enumerate(categories):
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name, sort_order=i))
                print(f'Created category: {name}')

        db.session.commit()
        print('Seed completed.')

if __name__ == '__main__':
    seed()
