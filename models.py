from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# 좋아요 관계 테이블 (Post)
post_likes = db.Table(
    'post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

# 좋아요 관계 테이블 (Comment)
comment_likes = db.Table(
    'comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.Text, default='')
    profile_image = db.Column(db.String(255), default='default_profile.jpg')
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    liked_posts = db.relationship('Post', secondary=post_likes, backref='liked_by')
    liked_comments = db.relationship('Comment', secondary=comment_likes, backref='liked_by')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def like_post(self, post):
        if not self.has_liked_post(post):
            self.liked_posts.append(post)
    
    def unlike_post(self, post):
        if self.has_liked_post(post):
            self.liked_posts.remove(post)
    
    def has_liked_post(self, post):
        return post in self.liked_posts
    
    def like_comment(self, comment):
        if not self.has_liked_comment(comment):
            self.liked_comments.append(comment)
    
    def unlike_comment(self, comment):
        if self.has_liked_comment(comment):
            self.liked_comments.remove(comment)
    
    def has_liked_comment(self, comment):
        return comment in self.liked_comments

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='일상')
    image_filename = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def get_likes_count(self):
        return len(self.liked_by)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_likes_count(self):
        return len(self.liked_by)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'comment', 'like', 'approval'
    message = db.Column(db.String(255), nullable=False)
    related_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    related_post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='received_notifications')
    related_user = db.relationship('User', foreign_keys=[related_user_id])
