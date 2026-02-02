# 공겜SNS (Team Social Network Service)

약 10명 규모의 팀원들이 일상을 공유할 수 있는 소셜 네트워크 애플리케이션입니다.

## 🎯 주요 기능

### 1. **사용자 관리**
- 회원가입 시 관리자 승인 필요
- 관리자만 회원을 승인/거절
- 개별 프로필 페이지 (수정 가능)
- 프로필 사진 업로드

### 2. **게시물**
- 게시물 작성 및 공유
- 이미지 업로드 지원
- 게시물 삭제 (작성자/관리자만)
- 게시물 좋아요

### 3. **댓글**
- 게시물에 댓글 작성
- 댓글 삭제 (작성자/관리자만)
- 댓글 좋아요

### 4. **알림 시스템**
- 새 댓글 알림
- 좋아요 알림
- 회원 승인 알림
- 미읽음 알림 배지

### 5. **관리자 기능**
- 회원 가입 승인/거절
- 부정적 게시물/댓글 삭제
- 사용자 관리 페이지

## 🚀 설치 및 실행

### 1. 필수 패키지 설치
```bash
cd team_sns
pip install -r requirements.txt
```

### 2. 기본 이미지 생성
```bash
python create_default_image.py
```

### 3. 애플리케이션 실행
```bash
python app.py
```

애플리케이션이 `http://127.0.0.1:5000`에서 실행됩니다.

## 📝 기본 계정

처음 실행 시 다음 관리자 계정이 자동으로 생성됩니다:
- **사용자명**: `admin`
- **비밀번호**: `admin123`

⚠️ **보안**: 프로덕션 환경에서는 반드시 비밀번호를 변경하세요!

## 📁 프로젝트 구조

```
team_sns/
├── app.py                 # 메인 애플리케이션
├── models.py              # 데이터베이스 모델
├── forms.py               # WTForms 폼
├── config.py              # 설정
├── requirements.txt       # 필수 패키지
├── create_default_image.py # 기본 이미지 생성
├── team_sns.db           # SQLite 데이터베이스 (생성됨)
├── templates/            # HTML 템플릿
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── waiting_approval.html
│   ├── feed.html
│   ├── post_detail.html
│   ├── profile.html
│   ├── edit_profile.html
│   ├── notifications.html
│   └── admin_users.html
└── static/               # 정적 파일
    ├── css/
    │   └── style.css
    ├── js/              # JavaScript 파일
    └── uploads/         # 이미지 저장소
```

## 🔧 사용 방법

### 회원가입
1. 로그인 페이지에서 "회원가입" 클릭
2. 필요한 정보 입력
3. 관리자 승인 대기

### 게시물 작성
1. 홈 피드에서 게시물 작성 폼 입력
2. 이미지 선택 (선택사항)
3. "게시" 버튼 클릭

### 프로필 관리
1. 우측 상단의 프로필 메뉴 클릭
2. "프로필 편집" 버튼 클릭
3. 정보 수정 및 프로필 사진 업로드

### 관리자 기능
1. 관리자로 로그인
2. 우측 상단의 "관리" 메뉴 클릭
3. 가입 신청자 승인/거절

## 📋 기술 스택

- **백엔드**: Flask (Python)
- **데이터베이스**: SQLite
- **프론트엔드**: HTML5, CSS3, Bootstrap 5, JavaScript
- **인증**: Flask-Login
- **폼 검증**: WTForms
- **이미지 처리**: Pillow

## 🔒 보안 기능

- 비밀번호 해싱 (werkzeug.security)
- CSRF 보호 (Flask-WTF)
- SQL 인젝션 방지 (SQLAlchemy ORM)
- 파일 업로드 검증

## 💡 커스터마이징

### 팀명 변경
`app.py`의 네비게이션 바 텍스트를 변경합니다.

### 최대 업로드 크기 변경
`config.py`의 `MAX_CONTENT_LENGTH` 값을 변경합니다.

### 허용 파일 형식 변경
`config.py`의 `ALLOWED_EXTENSIONS`를 수정합니다.

## ⚠️ 주의사항

1. **개발 환경**: `debug=True`로 실행되므로 프로덕션에서는 `debug=False`로 변경하세요.
2. **SECRET_KEY**: 프로덕션 환경에서는 환경 변수로 안전하게 관리하세요.
3. **데이터베이스**: SQLite는 소규모 팀용입니다. 대규모 확장 시 PostgreSQL 등을 추천합니다.

## 📞 지원

문제가 발생하면:
1. 브라우저 콘솔에서 오류 확인
2. 애플리케이션 로그 확인
3. 파이썬 코드 디버깅

## 📄 라이선스

프로젝트는 자유롭게 수정 및 배포할 수 있습니다.

---

**Happy Sharing! 🎉**
