# 🧵 스레드 콘텐츠 매핑 서비스

높은 참여도를 가진 스레드 콘텐츠를 분석하고, 사용자의 주제에 맞게 변환해주는 AI 기반 콘텐츠 매핑 서비스입니다.

## ✨ 주요 기능

- **높은 참여도 콘텐츠 분석**: 저장 수와 리포스트 수가 일정량 이상인 콘텐츠 자동 탐지
- **콘텐츠 패턴 분석**: 인기 콘텐츠의 구조와 형식 분석
- **AI 기반 콘텐츠 변환**: OpenAI GPT를 활용한 주제별 콘텐츠 변환
- **실시간 분석**: 카테고리별 트렌딩 콘텐츠 실시간 분석
- **사용자 친화적 UI**: 직관적이고 모던한 웹 인터페이스

## 🎯 서비스 핵심 로직

### 1. 콘텐츠 분석 기준
- **최소 참여도**: 저장 수 + 리포스트 수 ≥ 10개
- **참여도 점수**: 저장 수 + 리포스트 수 + 좋아요 수
- **카테고리별 분류**: 피트니스, 건강, 생산성, 요리, 기술 등

### 2. 콘텐츠 변환 프로세스
1. 원본 콘텐츠의 구조 분석
2. 이모지 사용 패턴 추출
3. 리스트/단계별 구성 파악
4. 사용자 주제에 맞는 새로운 콘텐츠 생성
5. 원본 스타일 유지하며 변환

### 3. 지원하는 콘텐츠 형식
- ✅ 리스트 형식 (번호/불릿 포인트)
- ✅ 비교 형식 (❌/✅ 패턴)
- ✅ 단계별 가이드
- ✅ 팁과 꿀팁 형식
- ✅ 레시피/방법론 형식

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd threads-content-mapper
```

### 2. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env` 파일에서 OpenAI API 키를 설정하세요:
```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 5. 서버 실행
```bash
python app.py
```

### 6. 브라우저에서 접속
```
http://localhost:5000
```

## 🛠️ 기술 스택

- **Backend**: Python, Flask
- **AI**: OpenAI GPT-3.5-turbo
- **Frontend**: HTML, CSS, JavaScript
- **데이터 처리**: Pandas, NumPy
- **HTTP 클라이언트**: Requests
- **환경 관리**: python-dotenv

## 📊 샘플 데이터

서비스에는 다음과 같은 시뮬레이션된 인기 콘텐츠가 포함되어 있습니다:

### 피트니스 카테고리
```
새해 운동 목표를 세우는 5가지 효과적인 방법 💪
1. 구체적인 목표 설정
2. 점진적 증가
3. 운동 파트너 찾기
4. 진행상황 기록
5. 보상 시스템 만들기
```
**참여도**: 저장 45개, 리포스트 28개, 좋아요 156개

### 건강 카테고리
```
집에서 만드는 간단한 디톡스 워터 레시피 🍋
✨ 레몬 + 오이 + 민트
✨ 자몽 + 로즈마리
✨ 베리 + 라임
하루 2L 마시면 피부도 좋아져요!
```
**참여도**: 저장 67개, 리포스트 34개, 좋아요 203개

## 💡 사용 방법

### 1. 주제 입력
원하는 주제를 입력하세요 (예: 독서, 투자, 언어학습 등)

### 2. 카테고리 선택 (선택사항)
분석할 특정 카테고리를 선택하거나 전체 카테고리에서 분석

### 3. 콘텐츠 분석
시스템이 높은 참여도의 콘텐츠를 자동으로 분석

### 4. 콘텐츠 변환
각 원본 콘텐츠를 클릭하여 사용자 주제로 변환

### 5. 결과 활용
변환된 콘텐츠를 스레드에 바로 사용

## 🔧 API 엔드포인트

### POST /analyze
콘텐츠 분석 요청
```json
{
  "user_topic": "독서",
  "topic_filter": "productivity"
}
```

### POST /transform
콘텐츠 변환 요청
```json
{
  "original_content": "원본 콘텐츠",
  "user_topic": "사용자 주제"
}
```

### GET /test
시스템 상태 확인

## 📈 향후 개발 계획

- [ ] 실제 Threads API 연동
- [ ] 더 다양한 콘텐츠 카테고리 추가
- [ ] 콘텐츠 성과 예측 기능
- [ ] 사용자 히스토리 저장
- [ ] 배치 변환 기능
- [ ] 다국어 지원

## ⚠️ 주의사항

- OpenAI API 키가 필요합니다
- 현재는 시뮬레이션된 데이터를 사용합니다
- 실제 서비스에서는 Threads API 연동이 필요합니다
- API 사용량에 따른 비용이 발생할 수 있습니다

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 GitHub Issues를 통해 연락해주세요.

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!
