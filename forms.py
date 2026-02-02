from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class SignUpForm(FlaskForm):
    username = StringField('사용자명', validators=[
        DataRequired(message='사용자명을 입력하세요'),
        Length(min=3, max=20, message='사용자명은 3-20자여야 합니다')
    ])
    email = StringField('이메일', validators=[
        DataRequired(message='이메일을 입력하세요'),
        Email(message='올바른 이메일 형식을 입력하세요')
    ])
    display_name = StringField('표시 이름', validators=[
        DataRequired(message='표시 이름을 입력하세요'),
        Length(min=2, max=50, message='표시 이름은 2-50자여야 합니다')
    ])
    password = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력하세요'),
        Length(min=6, message='비밀번호는 최소 6자 이상이어야 합니다')
    ])
    confirm_password = PasswordField('비밀번호 확인', validators=[
        DataRequired(message='비밀번호 확인을 입력하세요'),
        EqualTo('password', message='비밀번호가 일치하지 않습니다')
    ])
    submit = SubmitField('회원가입')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('이미 사용 중인 사용자명입니다')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('이미 가입된 이메일입니다')

class LoginForm(FlaskForm):
    username = StringField('사용자명', validators=[DataRequired(message='사용자명을 입력하세요')])
    password = PasswordField('비밀번호', validators=[DataRequired(message='비밀번호를 입력하세요')])
    submit = SubmitField('로그인')

class UpdateProfileForm(FlaskForm):
    display_name = StringField('표시 이름', validators=[
        DataRequired(message='표시 이름을 입력하세요'),
        Length(min=2, max=50)
    ])
    bio = TextAreaField('소개', validators=[Length(max=500)])
    profile_image = FileField('프로필 사진', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지 파일만 업로드 가능합니다')
    ])
    submit = SubmitField('저장')

class PostForm(FlaskForm):
    category = SelectField('카테고리', choices=[
        ('공지', '📢 공지'),
        ('일상', '☀️ 일상'),
        ('게임', '🎮 게임'),
        ('영화', '🎬 영화')
    ], validators=[DataRequired(message='카테고리를 선택하세요')])
    content = TextAreaField('무엇을 공유하시겠어요?', validators=[
        DataRequired(message='내용을 입력하세요'),
        Length(min=1, max=2000, message='내용은 1-2000자여야 합니다')
    ], render_kw={'rows': 4, 'placeholder': '당신의 일상을 공유하세요!'})
    image = FileField('이미지 추가', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지 파일만 업로드 가능합니다')
    ])
    submit = SubmitField('게시')

class CommentForm(FlaskForm):
    content = TextAreaField('댓글을 입력하세요', validators=[
        DataRequired(message='댓글을 입력하세요'),
        Length(min=1, max=500)
    ], render_kw={'rows': 2})
    submit = SubmitField('댓글 작성')
