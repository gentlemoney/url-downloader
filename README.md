# 🎥 소셜 미디어 비디오 다운로더

YouTube, TikTok, Instagram, Reddit, Twitter/X에서 비디오를 쉽게 다운로드할 수 있는 웹 서비스입니다.

## ✨ 주요 기능

- **다중 플랫폼 지원**: YouTube, TikTok, Instagram, Reddit, Twitter/X
- **빠른 다운로드**: 고속 서버로 빠른 다운로드
- **안전한 서비스**: 개인정보 보호 및 안전한 다운로드
- **모바일 친화적**: 모든 기기에서 편리하게 사용
- **실시간 플랫폼 감지**: URL 입력 시 자동으로 플랫폼 감지

## 🚀 지원 플랫폼

| 플랫폼 | 지원 콘텐츠 | 상태 |
|--------|-------------|------|
| YouTube | 비디오, 쇼츠 | ✅ |
| TikTok | 비디오 | ✅ |
| Instagram | Reels, Stories, Posts | ✅ |
| Reddit | 비디오, GIFs | ✅ |
| Twitter/X | 비디오 | ✅ |

## 🛠️ 기술 스택

- **Backend**: Python, Flask
- **Video Download**: yt-dlp
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render

## 📦 설치 및 실행

### 로컬 개발 환경

1. **저장소 클론**
```bash
git clone https://github.com/yourusername/social-media-downloader.git
cd social-media-downloader
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **서버 실행**
```bash
python app.py
```

5. **브라우저에서 접속**
```
http://localhost:3000
```

### Render 배포

1. **GitHub에 코드 푸시**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Render에서 새 서비스 생성**
   - Render 대시보드에서 "New +" 클릭
   - "Web Service" 선택
   - GitHub 저장소 연결
   - 다음 설정으로 구성:
     - **Name**: social-media-downloader
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Port**: 3000

## 📁 프로젝트 구조

```
social-media-downloader/
├── app.py                 # 메인 Flask 애플리케이션
├── requirements.txt       # Python 의존성
├── README.md             # 프로젝트 문서
├── downloads/            # 다운로드된 파일 저장소
└── .gitignore           # Git 무시 파일
```

## 🔧 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `PORT` | 서버 포트 | 3000 |
| `HOST` | 서버 호스트 | 0.0.0.0 |

## 🚀 사용 방법

1. **브라우저에서 서비스 접속**
2. **지원되는 플랫폼의 비디오 URL 입력**
3. **"다운로드" 버튼 클릭**
4. **다운로드 완료 후 파일 다운로드**

## 📝 사용 예시

### YouTube
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### TikTok
```
https://www.tiktok.com/@username/video/1234567890
```

### Instagram
```
https://www.instagram.com/p/ABC123/
```

### Reddit
```
https://www.reddit.com/r/videos/comments/123456/amazing_video/
```

### Twitter/X
```
https://twitter.com/username/status/1234567890
```

## 🔒 보안 및 개인정보

- 사용자 입력 URL은 서버에 저장되지 않습니다
- 다운로드된 파일은 임시로만 저장됩니다
- 개인정보 수집하지 않습니다

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## ⚠️ 면책 조항

이 서비스는 교육 및 개인 사용 목적으로만 제공됩니다. 저작권이 있는 콘텐츠의 다운로드는 해당 플랫폼의 이용약관을 준수해야 합니다. 사용자는 자신의 행동에 대한 책임을 져야 합니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 GitHub Issues를 통해 연락해주세요.

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요! 