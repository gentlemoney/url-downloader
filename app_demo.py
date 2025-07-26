from flask import Flask, render_template_string, request, jsonify
import os
import requests
import json
import re
from datetime import datetime
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = Flask(__name__)

class ThreadsAnalyzer:
    def __init__(self):
        self.min_engagement = 10  # 최소 참여도 임계값
        
    def analyze_trending_content(self, topic=None):
        """
        트렌딩 콘텐츠 분석 (실제로는 Threads API가 필요하지만 
        데모를 위해 시뮬레이션된 데이터 사용)
        """
        # 시뮬레이션된 인기 콘텐츠 데이터
        sample_threads = [
            {
                "id": "thread_1",
                "content": "새해 운동 목표를 세우는 5가지 효과적인 방법 💪\n1. 구체적인 목표 설정\n2. 점진적 증가\n3. 운동 파트너 찾기\n4. 진행상황 기록\n5. 보상 시스템 만들기",
                "saves": 45,
                "reposts": 28,
                "likes": 156,
                "topic": "fitness",
                "engagement_score": 229
            },
            {
                "id": "thread_2", 
                "content": "집에서 만드는 간단한 디톡스 워터 레시피 🍋\n✨ 레몬 + 오이 + 민트\n✨ 자몽 + 로즈마리\n✨ 베리 + 라임\n하루 2L 마시면 피부도 좋아져요!",
                "saves": 67,
                "reposts": 34,
                "likes": 203,
                "topic": "health",
                "engagement_score": 304
            },
            {
                "id": "thread_3",
                "content": "재택근무 생산성 높이는 꿀팁 🏠\n• 전용 작업공간 만들기\n• 뽀모도로 기법 활용\n• 자연광 최대한 활용\n• 정기적인 휴식시간\n• 일과 후 루틴 만들기",
                "saves": 89,
                "reposts": 52,
                "likes": 267,
                "topic": "productivity",
                "engagement_score": 408
            },
            {
                "id": "thread_4",
                "content": "요리 초보도 쉽게! 10분 파스타 레시피 🍝\n재료: 파스타면, 올리브오일, 마늘, 방울토마토, 바질\n1. 면 삶기 (8분)\n2. 마늘+토마토 볶기\n3. 파스타 넣고 섞기\n4. 바질 올리고 완성!",
                "saves": 124,
                "reposts": 78,
                "likes": 445,
                "topic": "cooking",
                "engagement_score": 647
            },
            {
                "id": "thread_5",
                "content": "스마트폰 배터리 수명 늘리는 방법 📱\n❌ 0%까지 방전 금지\n✅ 20-80% 사이 유지\n❌ 밤새 충전 금지\n✅ 발열 방지\n❌ 저품질 충전기 사용 금지",
                "saves": 156,
                "reposts": 92,
                "likes": 378,
                "topic": "tech",
                "engagement_score": 626
            }
        ]
        
        # 참여도가 높은 콘텐츠만 필터링
        high_engagement = [
            thread for thread in sample_threads 
            if (thread['saves'] + thread['reposts']) >= self.min_engagement
        ]
        
        # 주제별 필터링
        if topic:
            high_engagement = [
                thread for thread in high_engagement 
                if topic.lower() in thread['topic'].lower()
            ]
            
        return sorted(high_engagement, key=lambda x: x['engagement_score'], reverse=True)

class ContentTransformer:
    def __init__(self):
        pass
    
    def transform_content(self, original_content, user_topic, content_patterns):
        """
        원본 콘텐츠를 사용자 주제에 맞게 변환 (데모 버전 - 템플릿 기반)
        """
        # 원본 콘텐츠의 패턴 분석
        if "💪" in original_content and "목표" in original_content:
            # 운동 목표 패턴
            transformed = f"{user_topic} 마스터하기 위한 5가지 효과적인 방법 🎯\n1. 명확한 학습 목표 설정\n2. 단계별 점진적 학습\n3. 스터디 그룹 참여\n4. 진도 체크 및 기록\n5. 성취에 대한 자기 보상"
            
        elif "🍋" in original_content and "레시피" in original_content:
            # 레시피 패턴
            transformed = f"{user_topic} 활용 간단 레시피 모음 ✨\n✨ {user_topic} + 기본 재료\n✨ {user_topic} + 창의적 조합\n✨ {user_topic} + 실용적 활용\n매일 꾸준히 하면 실력이 늘어요!"
            
        elif "🏠" in original_content and "생산성" in original_content:
            # 생산성 팁 패턴
            transformed = f"{user_topic} 효율성 높이는 꿀팁 📚\n• 전용 {user_topic} 공간 조성\n• 집중 시간 블록 설정\n• 적절한 환경 조성\n• 규칙적인 휴식\n• 체계적인 일정 관리"
            
        elif "🍝" in original_content and "초보도" in original_content:
            # 초보자 가이드 패턴
            transformed = f"{user_topic} 초보자도 쉽게! 기본 가이드 📖\n준비물: 기본서, 노트, 펜, 시간, 열정\n1. 기초 개념 학습 (30분)\n2. 실습 예제 따라하기\n3. 복습 및 정리\n4. 응용 문제 도전!"
            
        elif "📱" in original_content and "수명" in original_content:
            # 유지/관리 팁 패턴
            transformed = f"{user_topic} 장기간 유지하는 방법 🔄\n❌ 과도한 집중 금지\n✅ 꾸준한 반복 학습\n❌ 완벽주의 금지\n✅ 점진적 발전\n❌ 외부 압박 금지"
            
        else:
            # 기본 템플릿
            transformed = f"{user_topic}에 관한 유용한 팁! 🌟\n\n이 콘텐츠는 {user_topic} 분야에 맞게 변환되었습니다.\n실제 서비스에서는 AI가 더욱 정교하게 변환해드립니다.\n\n✅ 구조 유지\n✅ 스타일 보존\n✅ 주제 맞춤"
            
        return transformed

# 전역 인스턴스
analyzer = ThreadsAnalyzer()
transformer = ContentTransformer()

# HTML 템플릿 (동일)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>스레드 콘텐츠 매핑 서비스</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
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
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        .demo-badge {
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 20px;
            margin-top: 15px;
            display: inline-block;
            font-size: 0.9rem;
        }
        .main-content {
            padding: 40px;
        }
        .input-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
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
            transition: border-color 0.3s;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .results-section {
            margin-top: 30px;
        }
        .thread-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.2s;
        }
        .thread-card:hover {
            transform: translateY(-2px);
        }
        .thread-stats {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.9rem;
            color: #666;
        }
        .stat {
            display: flex;
            align-items: center;
            gap: 5px;
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
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-radius: 50%;
            border-top: 3px solid #667eea;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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
            <div class="demo-badge">🚀 데모 모드 - 템플릿 기반 변환</div>
        </div>
        
        <div class="main-content">
            <div class="input-section">
                <form id="analysisForm">
                    <div class="form-group">
                        <label for="userTopic">변환하고 싶은 주제를 입력하세요</label>
                        <input type="text" id="userTopic" class="form-control" 
                               placeholder="예: 독서, 투자, 언어학습, 요리 등" required>
                    </div>
                    <div class="form-group">
                        <label for="topicFilter">분석할 카테고리 (선택사항)</label>
                        <select id="topicFilter" class="form-control">
                            <option value="">전체 카테고리</option>
                            <option value="fitness">피트니스</option>
                            <option value="health">건강</option>
                            <option value="productivity">생산성</option>
                            <option value="cooking">요리</option>
                            <option value="tech">기술</option>
                        </select>
                    </div>
                    <button type="submit" class="btn">🔍 인기 콘텐츠 분석 시작</button>
                </form>
            </div>
            
            <div id="results" class="results-section" style="display: none;">
                <h3>📊 높은 참여도 콘텐츠 분석 결과</h3>
                <div id="threadsContainer"></div>
            </div>
        </div>
    </div>
    
    <script>
        window.currentThreads = [];
        
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const userTopic = document.getElementById('userTopic').value;
            const topicFilter = document.getElementById('topicFilter').value;
            const resultsDiv = document.getElementById('results');
            const container = document.getElementById('threadsContainer');
            
            // 결과 영역 표시
            resultsDiv.style.display = 'block';
            container.innerHTML = '<div class="loading"><div class="spinner"></div>인기 콘텐츠를 분석하고 있습니다...</div>';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_topic: userTopic,
                        topic_filter: topicFilter
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                window.currentThreads = data.threads;
                displayResults(data.threads, userTopic);
                
            } catch (error) {
                container.innerHTML = `<div class="thread-card" style="border-color: #dc3545;">
                    <h4 style="color: #dc3545;">❌ 오류 발생</h4>
                    <p>${error.message}</p>
                </div>`;
            }
        });
        
        function displayResults(threads, userTopic) {
            const container = document.getElementById('threadsContainer');
            
            if (threads.length === 0) {
                container.innerHTML = '<div class="thread-card"><p>조건에 맞는 콘텐츠를 찾을 수 없습니다.</p></div>';
                return;
            }
            
            container.innerHTML = threads.map((thread, index) => `
                <div class="thread-card">
                    <div class="thread-stats">
                        <div class="stat">💾 저장: ${thread.saves}</div>
                        <div class="stat">🔄 리포스트: ${thread.reposts}</div>
                        <div class="stat">❤️ 좋아요: ${thread.likes}</div>
                        <div class="stat">📊 참여도: ${thread.engagement_score}</div>
                    </div>
                    
                    <h4>원본 콘텐츠 (${thread.topic})</h4>
                    <div class="thread-content">${thread.content}</div>
                    
                    <button class="btn transform-btn" onclick="transformContent(${index}, '${userTopic}')">
                        🔄 "${userTopic}" 주제로 변환하기
                    </button>
                    
                    <div id="transformed-${index}" style="display: none;">
                        <h4 style="margin-top: 20px;">✨ 변환된 콘텐츠</h4>
                        <div class="thread-content transformed-content" id="content-${index}"></div>
                    </div>
                </div>
            `).join('');
        }
        
        async function transformContent(index, userTopic) {
            const transformedDiv = document.getElementById(`transformed-${index}`);
            const contentDiv = document.getElementById(`content-${index}`);
            
            transformedDiv.style.display = 'block';
            contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div>콘텐츠를 변환하고 있습니다...</div>';
            
            try {
                const threads = window.currentThreads || [];
                const originalContent = threads[index].content;
                
                const response = await fetch('/transform', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        original_content: originalContent,
                        user_topic: userTopic
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                contentDiv.innerHTML = data.transformed_content;
                
            } catch (error) {
                contentDiv.innerHTML = `<div style="color: #dc3545;">❌ 변환 중 오류가 발생했습니다: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze_content():
    try:
        data = request.get_json()
        user_topic = data.get('user_topic', '')
        topic_filter = data.get('topic_filter', '')
        
        if not user_topic:
            return jsonify({'error': '주제를 입력해주세요.'}), 400
        
        # 트렌딩 콘텐츠 분석
        trending_threads = analyzer.analyze_trending_content(topic_filter)
        
        return jsonify({
            'threads': trending_threads,
            'user_topic': user_topic,
            'total_found': len(trending_threads)
        })
        
    except Exception as e:
        return jsonify({'error': f'분석 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/transform', methods=['POST'])
def transform_content():
    try:
        data = request.get_json()
        original_content = data.get('original_content', '')
        user_topic = data.get('user_topic', '')
        
        if not original_content or not user_topic:
            return jsonify({'error': '원본 콘텐츠와 주제가 필요합니다.'}), 400
        
        # 콘텐츠 변환 (데모 모드)
        transformed = transformer.transform_content(
            original_content, 
            user_topic, 
            {}  # 패턴 정보
        )
        
        return jsonify({
            'transformed_content': transformed,
            'original_content': original_content,
            'user_topic': user_topic
        })
        
    except Exception as e:
        return jsonify({'error': f'변환 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/test')
def test():
    """시스템 테스트용 엔드포인트"""
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'demo',
        'environment': {
            'flask_version': '3.1.1',
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        },
        'sample_analysis': {
            'total_threads': len(analyzer.analyze_trending_content()),
            'fitness_threads': len(analyzer.analyze_trending_content('fitness')),
            'tech_threads': len(analyzer.analyze_trending_content('tech'))
        }
    }
    
    return jsonify(test_results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print("🧵 스레드 콘텐츠 매핑 서비스가 시작됩니다! (데모 모드)")
    print(f"📍 주소: http://{host}:{port}")
    print("🚀 데모 모드: 템플릿 기반 콘텐츠 변환")
    
    app.run(host=host, port=port, debug=True)