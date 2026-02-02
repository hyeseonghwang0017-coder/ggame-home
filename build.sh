#!/usr/bin/env bash
# 데이터베이스 디렉토리 생성
mkdir -p instance

# 데이터베이스 초기화 및 관리자 계정 생성
python -c "
from app import app, db
from models import User

with app.app_context():
    db.create_all()
    
    # 관리자 계정이 없으면 생성
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@ggame.com',
            display_name='관리자',
            is_admin=True,
            is_approved=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('관리자 계정이 생성되었습니다.')
    else:
        print('관리자 계정이 이미 존재합니다.')
"
