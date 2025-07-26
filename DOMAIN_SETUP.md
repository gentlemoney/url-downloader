# 🌐 커스텀 도메인 설정 가이드

`gptkimisa.com` 도메인에 소셜 미디어 다운로더 서비스를 연결하는 방법입니다.

## 📋 사전 준비

1. **도메인 소유권**: `gptkimisa.com` 도메인을 소유하고 있어야 합니다
2. **도메인 제공업체**: DNS 설정을 변경할 수 있는 권한이 있어야 합니다
3. **Render 서비스**: 배포된 웹 서비스가 있어야 합니다

## 🔧 Render 설정

### 1. Render 서비스 생성

1. https://render.com 접속
2. "New +" → "Web Service" 클릭
3. GitHub 저장소 연결: `gentlemoney/url-downloader`
4. 서비스 설정:
   ```
   Name: social-media-downloader
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

### 2. 커스텀 도메인 추가

1. Render 대시보드에서 서비스 클릭
2. "Settings" 탭으로 이동
3. "Custom Domains" 섹션에서 "Add Domain" 클릭
4. 도메인 입력:
   - `gptkimisa.com` (루트 도메인)
   - `www.gptkimisa.com` (서브도메인)

## 🌍 DNS 설정

도메인 제공업체의 DNS 관리 페이지에서 다음 레코드를 추가하세요:

### A 레코드 (루트 도메인용)
```
Type: A
Name: @ (또는 비워두기)
Value: 76.76.19.19
TTL: 3600
```

### CNAME 레코드 (www 서브도메인용)
```
Type: CNAME
Name: www
Value: gptkimisa.com
TTL: 3600
```

### 추가 A 레코드 (필요시)
```
Type: A
Name: @
Value: 76.76.19.19
TTL: 3600
```

## 🔒 SSL 인증서 설정

Render는 자동으로 SSL 인증서를 제공합니다:

- **자동 HTTPS**: 모든 트래픽이 HTTPS로 리다이렉트
- **Let's Encrypt**: 무료 SSL 인증서
- **자동 갱신**: 90일마다 자동 갱신

## ⏱️ 설정 완료 시간

- **DNS 전파**: 24-48시간 (보통 몇 시간 내)
- **SSL 인증서**: 몇 분 내 자동 발급
- **도메인 연결**: DNS 전파 완료 후 즉시

## 🔍 설정 확인

### 1. DNS 전파 확인
```bash
# 터미널에서 확인
nslookup gptkimisa.com
dig gptkimisa.com
```

### 2. 웹사이트 접속 테스트
- http://gptkimisa.com
- https://gptkimisa.com
- http://www.gptkimisa.com
- https://www.gptkimisa.com

### 3. SSL 인증서 확인
브라우저에서 자물쇠 아이콘 클릭하여 인증서 정보 확인

## 🛠️ 문제 해결

### DNS 전파 지연
- 최대 48시간 대기
- `nslookup` 명령어로 확인
- 도메인 제공업체에 문의

### SSL 인증서 오류
- DNS 전파 완료 후 24시간 대기
- Render 대시보드에서 SSL 상태 확인
- 도메인 설정 재확인

### 접속 불가
- DNS 레코드 정확성 확인
- Render 서비스 상태 확인
- 방화벽 설정 확인

## 📱 서브도메인 설정 (선택사항)

추가 서브도메인을 원한다면:

### CNAME 레코드 추가
```
Type: CNAME
Name: download
Value: gptkimisa.com
TTL: 3600
```

이후 `download.gptkimisa.com`으로 접속 가능

## 🔄 도메인 변경 시

1. **새 도메인 추가**: Render에서 새 도메인 설정
2. **DNS 업데이트**: 새 도메인에 대한 DNS 레코드 추가
3. **기존 도메인 제거**: 설정 완료 후 기존 도메인 제거

## 📊 모니터링

### 도메인 상태 확인
- Render 대시보드에서 도메인 상태 모니터링
- SSL 인증서 만료일 확인
- 트래픽 통계 확인

### 알림 설정
- 도메인 연결 실패 알림
- SSL 인증서 만료 알림
- 서비스 다운타임 알림

---

🎉 설정이 완료되면 `https://gptkimisa.com`으로 접속하여 서비스를 이용할 수 있습니다! 