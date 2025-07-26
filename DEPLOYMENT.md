# 🚀 배포 가이드

이 문서는 소셜 미디어 비디오 다운로더를 GitHub와 Render에 배포하는 방법을 설명합니다.

## 📋 사전 준비

1. **GitHub 계정**
2. **Render 계정** (https://render.com)
3. **로컬 Git 설정**

## 🔧 GitHub 설정

### 1. GitHub 저장소 생성

1. GitHub에 로그인
2. "New repository" 클릭
3. 저장소 설정:
   - **Repository name**: `social-media-downloader`
   - **Description**: `Multi-platform social media video downloader`
   - **Visibility**: Public (또는 Private)
   - **Initialize with**: README 체크 해제

### 2. 로컬 저장소를 GitHub에 연결

```bash
# 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/social-media-downloader.git

# 메인 브랜치로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

## 🌐 Render 배포

### 1. Render 계정 생성

1. https://render.com 접속
2. GitHub 계정으로 로그인

### 2. 새 Web Service 생성

1. Render 대시보드에서 "New +" 클릭
2. "Web Service" 선택
3. GitHub 저장소 연결

### 3. 서비스 설정

| 설정 항목 | 값 |
|----------|-----|
| **Name** | social-media-downloader |
| **Environment** | Python 3 |
| **Region** | Frankfurt (EU) 또는 가까운 지역 |
| **Branch** | main |
| **Root Directory** | (비워두기) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |

### 4. 환경 변수 설정

Render 대시보드에서 "Environment" 탭에서 다음 변수 설정:

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `PORT` | 10000 | Render에서 제공하는 포트 |
| `HOST` | 0.0.0.0 | 모든 IP에서 접근 허용 |

### 5. 배포 실행

1. "Create Web Service" 클릭
2. 배포 완료까지 대기 (약 2-3분)
3. 제공된 URL로 접속 테스트

## 🔍 배포 확인

### 1. 로그 확인

Render 대시보드에서 "Logs" 탭에서 배포 로그 확인:

```
[INFO] Starting build...
[INFO] Installing dependencies...
[INFO] Build completed successfully
[INFO] Starting service...
[INFO] Service is running on port 10000
```

### 2. 서비스 테스트

1. 제공된 URL로 접속
2. YouTube 링크로 테스트 다운로드
3. 모든 기능 정상 작동 확인

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. 빌드 실패
```
Error: Could not find a version that satisfies the requirement
```
**해결책**: requirements.txt의 버전을 최신으로 업데이트

#### 2. 포트 오류
```
Error: Port already in use
```
**해결책**: 환경 변수 `PORT`를 Render에서 제공하는 포트로 설정

#### 3. 메모리 부족
```
Error: Memory limit exceeded
```
**해결책**: Render 플랜을 업그레이드하거나 코드 최적화

### 로그 확인 방법

1. Render 대시보드 → 해당 서비스 → "Logs" 탭
2. 실시간 로그 스트림 확인
3. 오류 메시지 분석

## 🔄 업데이트 배포

코드 변경 후 새로운 배포:

```bash
# 로컬에서 변경사항 커밋
git add .
git commit -m "Update: 새로운 기능 추가"
git push origin main

# Render에서 자동 배포 시작
```

## 📊 모니터링

### 1. 성능 모니터링

- Render 대시보드에서 CPU, 메모리 사용량 확인
- 응답 시간 모니터링

### 2. 오류 모니터링

- 로그에서 오류 패턴 확인
- 사용자 피드백 수집

## 🔒 보안 고려사항

1. **환경 변수**: 민감한 정보는 환경 변수로 관리
2. **HTTPS**: Render는 자동으로 HTTPS 제공
3. **Rate Limiting**: 과도한 요청 방지
4. **파일 정리**: 다운로드된 파일 자동 삭제

## 💰 비용 최적화

### 무료 플랜 제한사항

- **월 사용량**: 750시간
- **메모리**: 512MB
- **CPU**: 0.1 CPU

### 비용 절약 팁

1. **자동 스케일링**: 트래픽이 적을 때 자동 종료
2. **캐싱**: CDN 사용으로 서버 부하 감소
3. **최적화**: 코드 최적화로 리소스 사용량 감소

## 📞 지원

배포 중 문제가 발생하면:

1. **GitHub Issues**: 버그 리포트
2. **Render Support**: 배포 관련 문제
3. **문서 확인**: README.md 및 이 가이드 참조

---

🎉 배포가 완료되면 전 세계 어디서나 접근 가능한 웹 서비스가 됩니다! 