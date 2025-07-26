from flask import Flask, render_template_string, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

class ThreadsAnalyzer:
    def __init__(self):
        self.min_engagement = 10
        
    def analyze_trending_content(self, topic=None):
        sample_threads = [
            {
                "id": "thread_1",
                "content": "새해 운동 목표를 세우는 5가지 효과적인 방법 💪\\n1. 구체적인 목표 설정\\n2. 점진적 증가\\n3. 운동 파트너 찾기\\n4. 진행상황 기록\\n5. 보상 시스템 만들기",
                "saves": 45,
                "reposts": 28,
                "likes": 156,
                "topic": "fitness",
                "engagement_score": 229
            },
            {
                "id": "thread_2", 
                "content": "집에서 만드는 간단한 디톡스 워터 레시피 🍋\\n✨ 레몬 + 오이 + 민트\\n✨ 자몽 + 로즈마리\\n✨ 베리 + 라임\\n하루 2L 마시면 피부도 좋아져요!",
                "saves": 67,
                "reposts": 34,
                "likes": 203,
                "topic": "health",
                "engagement_score": 304
            },
            {
                "id": "thread_3",
                "content": "재택근무 생산성 높이는 꿀팁 🏠\\n• 전용 작업공간 만들기\\n• 뽀모도로 기법 활용\\n• 자연광 최대한 활용\\n• 정기적인 휴식시간\\n• 일과 후 루틴 만들기",
                "saves": 89,
                "reposts": 52,
                "likes": 267,
                "topic": "productivity",
                "engagement_score": 408
            }
        ]
        
        high_engagement = [thread for thread in sample_threads if (thread['saves'] + thread['reposts']) >= self.min_engagement]
        
        if topic:
            high_engagement = [thread for thread in high_engagement if topic.lower() in thread['topic'].lower()]
            
        return sorted(high_engagement, key=lambda x: x['engagement_score'], reverse=True)

class ContentTransformer:
    def transform_content(self, original_content, user_topic, content_patterns):
        if "💪" in original_content and "목표" in original_content:
            return f"{user_topic} 마스터하기 위한 5가지 효과적인 방법 🎯\\n1. 명확한 학습 목표 설정\\n2. 단계별 점진적 학습\\n3. 스터디 그룹 참여\\n4. 진도 체크 및 기록\\n5. 성취에 대한 자기 보상"
        elif "🍋" in original_content and "레시피" in original_content:
            return f"{user_topic} 활용 간단 가이드 ✨\\n✨ {user_topic} + 기본 원리\\n✨ {user_topic} + 실전 활용\\n✨ {user_topic} + 고급 기법\\n매일 꾸준히 하면 실력이 늘어요!"
        elif "🏠" in original_content and "생산성" in original_content:
            return f"{user_topic} 효율성 높이는 꿀팁 📚\\n• 전용 {user_topic} 공간 조성\\n• 집중 시간 블록 설정\\n• 적절한 환경 조성\\n• 규칙적인 휴식\\n• 체계적인 일정 관리"
        else:
            return f"{user_topic}에 관한 유용한 팁! 🌟\\n\\n이 콘텐츠는 {user_topic} 분야에 맞게 변환되었습니다.\\n실제 서비스에서는 AI가 더욱 정교하게 변환해드립니다.\\n\\n✅ 구조 유지\\n✅ 스타일 보존\\n✅ 주제 맞춤"

analyzer = ThreadsAnalyzer()
transformer = ContentTransformer()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>스레드 콘텐츠 매핑 서비스</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .demo-badge {
                background: rgba(255,255,255,0.2);
                padding: 8px 15px;
                border-radius: 20px;
                margin-top: 15px;
                display: inline-block;
                font-size: 0.9rem;
            }
            .main-content { padding: 40px; }
            .input-section {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 30px;
            }
            .form-group { margin-bottom: 20px; }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            .form-control {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 1rem;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 10px;
                font-size: 1rem;
                cursor: pointer;
            }
            .thread-card {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            }
            .thread-stats {
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
                font-size: 0.9rem;
                color: #666;
            }
            .thread-content {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                border-left: 4px solid #667eea;
                white-space: pre-wrap;
            }
            .transformed-content {
                background: #e8f5e8;
                border-left-color: #28a745;
            }
            .transform-btn {
                background: #28a745;
                font-size: 0.9rem;
                padding: 8px 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧵 스레드 콘텐츠 매핑</h1>
                <p>높은 참여도의 콘텐츠를 분석하고 당신의 주제에 맞게 변환해드립니다</p>
                <div class="demo-badge">🚀 데모 모드</div>
            </div>
            
            <div class="main-content">
                <div class="input-section">
                    <form id="analysisForm">
                        <div class="form-group">
                            <label for="userTopic">변환하고 싶은 주제를 입력하세요</label>
                            <input type="text" id="userTopic" class="form-control" 
                                   placeholder="예: 독서, 투자, 언어학습, 요리 등" required>
                        </div>
                        <button type="submit" class="btn">🔍 인기 콘텐츠 분석 시작</button>
                    </form>
                </div>
                
                <div id="results" style="display: none;">
                    <h3>📊 높은 참여도 콘텐츠 분석 결과</h3>
                    <div id="threadsContainer"></div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('analysisForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const userTopic = document.getElementById('userTopic').value;
                const resultsDiv = document.getElementById('results');
                const container = document.getElementById('threadsContainer');
                
                resultsDiv.style.display = 'block';
                container.innerHTML = '<p>분석 중...</p>';
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_topic: userTopic })
                    });
                    
                    const data = await response.json();
                    displayResults(data.threads, userTopic);
                    
                } catch (error) {
                    container.innerHTML = '<p>오류가 발생했습니다: ' + error.message + '</p>';
                }
            });
            
            function displayResults(threads, userTopic) {
                const container = document.getElementById('threadsContainer');
                
                container.innerHTML = threads.map((thread, index) => 
                    '<div class="thread-card">' +
                        '<div class="thread-stats">' +
                            '<span>💾 저장: ' + thread.saves + '</span>' +
                            '<span>🔄 리포스트: ' + thread.reposts + '</span>' +
                            '<span>❤️ 좋아요: ' + thread.likes + '</span>' +
                            '<span>📊 참여도: ' + thread.engagement_score + '</span>' +
                        '</div>' +
                        '<h4>원본 콘텐츠 (' + thread.topic + ')</h4>' +
                        '<div class="thread-content">' + thread.content + '</div>' +
                        '<button class="btn transform-btn" onclick="transformContent(' + index + ', \'' + userTopic + '\', \'' + thread.content.replace(/'/g, "\\'") + '\')">' +
                            '🔄 "' + userTopic + '" 주제로 변환하기' +
                        '</button>' +
                        '<div id="transformed-' + index + '" style="display: none;">' +
                            '<h4 style="margin-top: 20px;">✨ 변환된 콘텐츠</h4>' +
                            '<div class="thread-content transformed-content" id="content-' + index + '"></div>' +
                        '</div>' +
                    '</div>'
                ).join('');
            }
            
            async function transformContent(index, userTopic, originalContent) {
                const transformedDiv = document.getElementById('transformed-' + index);
                const contentDiv = document.getElementById('content-' + index);
                
                transformedDiv.style.display = 'block';
                contentDiv.innerHTML = '변환 중...';
                
                try {
                    const response = await fetch('/transform', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            original_content: originalContent,
                            user_topic: userTopic
                        })
                    });
                    
                    const data = await response.json();
                    contentDiv.innerHTML = data.transformed_content;
                    
                } catch (error) {
                    contentDiv.innerHTML = '변환 중 오류가 발생했습니다.';
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze_content():
    try:
        data = request.get_json()
        user_topic = data.get('user_topic', '')
        
        if not user_topic:
            return jsonify({'error': '주제를 입력해주세요.'}), 400
        
        trending_threads = analyzer.analyze_trending_content()
        
        return jsonify({
            'threads': trending_threads,
            'user_topic': user_topic,
            'total_found': len(trending_threads)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transform', methods=['POST'])
def transform_content():
    try:
        data = request.get_json()
        original_content = data.get('original_content', '')
        user_topic = data.get('user_topic', '')
        
        if not original_content or not user_topic:
            return jsonify({'error': '원본 콘텐츠와 주제가 필요합니다.'}), 400
        
        transformed = transformer.transform_content(original_content, user_topic, {})
        
        return jsonify({
            'transformed_content': transformed,
            'original_content': original_content,
            'user_topic': user_topic
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test():
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'mode': 'demo',
        'status': 'running',
        'threads_count': len(analyzer.analyze_trending_content())
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🧵 스레드 콘텐츠 매핑 서비스 시작! (포트: {port})")
    print("🚀 데모 모드: 템플릿 기반 콘텐츠 변환")
    print(f"📍 주소: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=True)
