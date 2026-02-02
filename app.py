from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime
from PIL import Image
from io import BytesIO

from config import Config
from models import db, User, Post, Comment, Notification
from forms import SignUpForm, LoginForm, UpdateProfileForm, PostForm, CommentForm

app = Flask(__name__)
app.config.from_object(Config)

# 업로드 폴더 생성
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# 기본 프로필 이미지 생성
try:
    from create_default_image import *
except ImportError:
    pass

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '로그인이 필요합니다'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 오류 핸들러
@app.errorhandler(500)
def internal_error(error):
    print(f"500 Error: {error}")
    import traceback
    traceback.print_exc()
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('관리자만 접근할 수 있습니다', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def approved_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_approved:
            flash('아직 관리자의 승인이 필요합니다', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_image(file, prefix='post'):
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        img = Image.open(file)
        img.thumbnail((1200, 1200))
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{prefix}_{timestamp}_{file.filename}")
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        img.save(filepath)
        return filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

# 데이터베이스 초기화
with app.app_context():
    db.create_all()
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@teamsns.com',
            display_name='관리자',
            is_admin=True,
            is_approved=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("관리자 계정이 생성되었습니다. (username: admin, password: admin123)")

# ===== 인증 관련 라우트 =====
@app.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.is_approved:
            return redirect(url_for('waiting_approval'))
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            display_name=form.display_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # 관리자에게 알림
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            notification = Notification(
                user_id=admin.id,
                type='approval',
                message=f'{form.display_name.data}님이 가입 승인을 기다리고 있습니다',
                related_user_id=user.id
            )
            db.session.add(notification)
            db.session.commit()
        
        flash('회원가입 신청이 완료되었습니다. 관리자의 승인을 기다려주세요', 'info')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_approved and not user.is_admin:
                flash('아직 관리자의 승인이 필요합니다', 'warning')
                return redirect(url_for('login'))
            
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('feed'))
        else:
            flash('사용자명 또는 비밀번호가 잘못되었습니다', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다', 'info')
    return redirect(url_for('login'))

@app.route('/waiting-approval')
@login_required
def waiting_approval():
    if current_user.is_approved:
        return redirect(url_for('feed'))
    return render_template('waiting_approval.html')

# ===== 피드 관련 라우트 =====
@app.route('/feed')
@login_required
@approved_required
def feed():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    
    if category and category in ['공지', '일상', '게임', '영화']:
        posts = Post.query.filter_by(category=category).order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    else:
        posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    
    form = PostForm()
    
    return render_template('feed.html', posts=posts, form=form, current_category=category)

@app.route('/post/create', methods=['POST'])
@login_required
@approved_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_filename = save_image(form.image.data, 'post')
        
        post = Post(
            content=form.content.data,
            category=form.category.data,
            image_filename=image_filename,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        
        flash('게시물이 작성되었습니다', 'success')
    
    return redirect(url_for('feed'))

@app.route('/post/<int:post_id>')
@login_required
@approved_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    return render_template('post_detail.html', post=post, form=form)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('권한이 없습니다', 'danger')
        return redirect(url_for('feed'))
    
    db.session.delete(post)
    db.session.commit()
    
    flash('게시물이 삭제되었습니다', 'success')
    return redirect(url_for('feed'))

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
@approved_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if current_user.has_liked_post(post):
        current_user.unlike_post(post)
        liked = False
    else:
        current_user.like_post(post)
        liked = True
        
        # 게시물 작성자에게 알림
        if post.author.id != current_user.id:
            notification = Notification(
                user_id=post.author.id,
                type='like',
                message=f'{current_user.display_name}님이 당신의 게시물을 좋아합니다',
                related_user_id=current_user.id,
                related_post_id=post.id
            )
            db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': post.get_likes_count()
    })

# ===== 댓글 관련 라우트 =====
@app.route('/post/<int:post_id>/comment/add', methods=['POST'])
@login_required
@approved_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        
        # 게시물 작성자에게 알림
        if post.author.id != current_user.id:
            notification = Notification(
                user_id=post.author.id,
                type='comment',
                message=f'{current_user.display_name}님이 당신의 게시물에 댓글을 남겼습니다',
                related_user_id=current_user.id,
                related_post_id=post.id
            )
            db.session.add(notification)
            db.session.commit()
        
        flash('댓글이 작성되었습니다', 'success')
    
    return redirect(url_for('view_post', post_id=post.id))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('권한이 없습니다', 'danger')
        return redirect(url_for('view_post', post_id=post_id))
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('댓글이 삭제되었습니다', 'success')
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
@approved_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if current_user.has_liked_comment(comment):
        current_user.unlike_comment(comment)
        liked = False
    else:
        current_user.like_comment(comment)
        liked = True
        
        # 댓글 작성자에게 알림
        if comment.author.id != current_user.id:
            notification = Notification(
                user_id=comment.author.id,
                type='like',
                message=f'{current_user.display_name}님이 당신의 댓글을 좋아합니다',
                related_user_id=current_user.id,
                related_post_id=comment.post_id
            )
            db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': comment.get_likes_count()
    })

# ===== 프로필 관련 라우트 =====
@app.route('/profile/<int:user_id>')
@login_required
@approved_required
def view_profile(user_id):
    try:
        user = User.query.get_or_404(user_id)
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
        
        return render_template('profile.html', user=user, posts=posts)
    except Exception as e:
        print(f"Profile Error: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('프로필을 불러올 수 없습니다.', 'danger')
        return redirect(url_for('feed'))

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    
    if form.validate_on_submit():
        current_user.display_name = form.display_name.data
        current_user.bio = form.bio.data
        
        # 새로운 이미지가 업로드된 경우에만 업데이트
        if form.profile_image.data:
            image_filename = save_image(form.profile_image.data, 'profile')
            if image_filename:
                # 기존 이미지 삭제 (default_profile.jpg 제외)
                if current_user.profile_image and current_user.profile_image != 'default_profile.jpg':
                    old_image_path = os.path.join(Config.UPLOAD_FOLDER, current_user.profile_image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                current_user.profile_image = image_filename
        
        db.session.commit()
        flash('프로필이 업데이트되었습니다', 'success')
        return redirect(url_for('view_profile', user_id=current_user.id))
    
    elif request.method == 'GET':
        form.display_name.data = current_user.display_name
        form.bio.data = current_user.bio
    
    return render_template('edit_profile.html', form=form)

# ===== 알림 관련 라우트 =====
@app.route('/notifications')
@login_required
def notifications():
    notifications_list = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications.html', notifications=notifications_list[:20])

@app.route('/notification/<int:notification_id>/read', methods=['POST'])
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'success': False}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/notifications/unread-count')
@login_required
def get_unread_notifications_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

# ===== 관리자 라우트 =====
@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'pending')
    
    if filter_type == 'pending':
        users = User.query.filter_by(is_approved=False, is_admin=False).paginate(page=page, per_page=10)
    elif filter_type == 'approved':
        users = User.query.filter_by(is_approved=True, is_admin=False).paginate(page=page, per_page=10)
    else:
        users = User.query.filter_by(is_admin=False).paginate(page=page, per_page=10)
    
    return render_template('admin_users.html', users=users, filter_type=filter_type)

@app.route('/admin/user/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'success': False, 'message': '관리자는 승인할 수 없습니다'}), 400
    
    user.is_approved = True
    
    notification = Notification(
        user_id=user.id,
        type='approval',
        message='관리자님이 당신의 가입을 승인했습니다! 이제 팀 커뮤니티를 즐길 수 있습니다.',
        related_user_id=current_user.id
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/user/<int:user_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'success': False, 'message': '관리자는 거절할 수 없습니다'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
