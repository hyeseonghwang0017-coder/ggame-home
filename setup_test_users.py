#!/usr/bin/env python
import sys
sys.path.insert(0, '/Users/hyeseong/Documents/파이썬 실습/team_sns')
from app import app, db, User, Post
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if test user exists
    test_user = User.query.filter_by(username='testuser').first()
    if not test_user:
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            display_name='Test User',
            bio='This is a test user',
            is_approved=True,
            is_admin=False
        )
        db.session.add(test_user)
        db.session.commit()
        print('Test user created successfully!')
    else:
        print(f'Test user already exists with ID: {test_user.id}')
    
    # Approve admin if not already
    admin = User.query.filter_by(username='admin').first()
    if admin and not admin.is_approved:
        admin.is_approved = True
        db.session.commit()
        print('Admin user approved!')
    
    # Create a test post for the test user
    test_user = User.query.filter_by(username='testuser').first()
    if test_user:
        post_count = Post.query.filter_by(user_id=test_user.id).count()
        if post_count == 0:
            post = Post(
                content='This is a test post! 안녕하세요! 🎮',
                category='게임',
                user_id=test_user.id
            )
            db.session.add(post)
            db.session.commit()
            print('Test post created successfully!')
        else:
            print(f'Test user already has {post_count} post(s)')
