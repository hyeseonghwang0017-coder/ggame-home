from PIL import Image, ImageDraw
import os

# static/uploads 폴더 생성
uploads_dir = os.path.join(os.path.dirname(__file__), 'static/uploads')
os.makedirs(uploads_dir, exist_ok=True)

# 기본 프로필 이미지 생성
img = Image.new('RGB', (200, 200), color='#e9ecef')
draw = ImageDraw.Draw(img)

# 원 그리기
draw.ellipse([25, 25, 175, 175], fill='#dee2e6', outline='#adb5bd', width=3)

# 저장
img.save(os.path.join(uploads_dir, 'default_profile.jpg'))
print("기본 프로필 이미지가 생성되었습니다.")
