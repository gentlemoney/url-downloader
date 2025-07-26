from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import uuid
import logging
import requests
import json
import re
from pytube import YouTube
import sys

from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Render 환경 자동 감지
IS_SERVER_ENV = (
    os.environ.get('RENDER') or 
    'onrender.com' in os.environ.get('HOSTNAME', '') or
    os.environ.get('PORT') or
    'cursor' in os.environ.get('HOSTNAME', '').lower() or
    os.path.exists('/.dockerenv')
)

if IS_SERVER_ENV:
    os.environ['SERVER_ENV'] = 'true'
    print("🚀 서버 환경 감지됨 - 특별 설정 적용", flush=True)

# 강화된 로깅 설정 (Render용)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Render 로그 출력 확인
print("🔍 로깅 시스템 초기화 완료", flush=True)
logger.info("Flask 앱 시작 중...")

# 다운로드 폴더 설정 - Render 환경에 맞게 조정
if IS_SERVER_ENV:
    DOWNLOAD_FOLDER = '/tmp/downloads'
else:
    DOWNLOAD_FOLDER = os.path.abspath('downloads')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER, mode=0o755)
    print(f"📁 다운로드 폴더 생성: {DOWNLOAD_FOLDER}", flush=True)

# 폴더 권한 확인
print(f"📋 폴더 권한 확인: {oct(os.stat(DOWNLOAD_FOLDER).st_mode)[-3:]}", flush=True)
print(f"📍 현재 작업 디렉토리: {os.getcwd()}", flush=True)
print(f"📁 절대 경로: {DOWNLOAD_FOLDER}", flush=True)
print(f"🌐 서버 환경: {IS_SERVER_ENV}", flush=True)

def download_youtube_with_pytube(url, outtmpl):
    """pytube를 사용하여 YouTube 비디오를 다운로드합니다."""
    try:
        print(f"📺 pytube로 YouTube 다운로드 시작: {url}", flush=True)
        logger.info(f"pytube로 YouTube 다운로드 시작: {url}")
        
        # YouTube 객체 생성
        yt = YouTube(url)
        
        # 최고 품질의 MP4 스트림 선택
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            raise Exception("적절한 스트림을 찾을 수 없습니다")
        
        # 파일명 생성
        safe_title = re.sub(r'[^\w\s-]', '', yt.title).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = os.path.join(DOWNLOAD_FOLDER, f"{safe_title}.mp4")
        
        print(f"💾 다운로드할 파일명: {filename}", flush=True)
        
        # 다운로드
        stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{safe_title}.mp4")
        
        print(f"✅ pytube 다운로드 완료: {filename}", flush=True)
        logger.info(f"pytube 다운로드 완료: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ pytube 오류: {str(e)}", flush=True)
        logger.error(f"pytube 오류: {str(e)}")
        raise e

def create_youtube_cookies():
    """YouTube용 가짜 쿠키 파일을 생성합니다."""
    import tempfile
    import os
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            cookie_content = """# Netscape HTTP Cookie File
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	FALSE	0	VISITOR_INFO1_LIVE	fPQ4jCL6EiE
.youtube.com	TRUE	/	FALSE	0	YSC	DjdQqy9i8_w
.youtube.com	TRUE	/	FALSE	0	PREF	f4=4000000
youtube.com	FALSE	/	FALSE	0	GPS	1
"""
            f.write(cookie_content)
            print(f"🍪 쿠키 파일 생성: {f.name}", flush=True)
            return f.name
    except Exception as e:
        print(f"❌ 쿠키 파일 생성 실패: {str(e)}", flush=True)
        logger.error(f"쿠키 파일 생성 실패: {str(e)}")
        return None

fake_cookies = create_youtube_cookies()

def get_server_optimized_options(platform, outtmpl):
    """서버 환경에 최적화된 yt-dlp 설정을 반환합니다."""
    import time
    import random
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    selected_ua = random.choice(user_agents)
    print(f"🔧 선택된 User-Agent: {selected_ua[:50]}...", flush=True)
    
    base_opts = {
        'format': 'best[height<=720]/best[height<=480]/worst',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'nocheckcertificate': True,
        'socket_timeout': 60,
        'retries': 10,
        'fragment_retries': 10,
        'extractor_retries': 10,
        'file_access_retries': 5,
        'user_agent': selected_ua,
        'no_playlist': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'embed_chapters': False,
        'embed_info_json': False,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': selected_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    }
    
    if platform == 'YouTube':
        base_opts.update({
            'format': 'best[height<=720]/best[height<=480]/worst',
            'extractor_retries': 15,
            'sleep_interval': random.uniform(0.5, 2),
            'max_sleep_interval': 3,
            'youtube_include_dash_manifest': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writedescription': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'skip_unavailable_fragments': True,
            'extractor_args': {
                'youtube': {
                    'construct_dash': False,
                    'skip': ['hls', 'dash'],
                    'player_skip': ['configs'],
                }
            },
            'http_headers': {
                **base_opts['http_headers'],
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
                'X-YouTube-Client-Name': '1',
                'X-YouTube-Client-Version': '2.20231214.01.00'
            },
            'cookiefile': fake_cookies if fake_cookies else None
        })
    
    print(f"⚙️ yt-dlp 옵션 설정 완료 (플랫폼: {platform})", flush=True)
    return base_opts

def detect_platform(url):
    """URL에서 플랫폼을 감지합니다."""
    try:
        parsed = urlparse(url.lower())
        domain = parsed.netloc.lower()
        
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'YouTube', 'fab fa-youtube', '#FF0000'
        elif 'tiktok.com' in domain:
            return 'TikTok', 'fab fa-tiktok', '#000000'
        elif 'instagram.com' in domain:
            return 'Instagram', 'fab fa-instagram', '#E4405F'
        elif 'reddit.com' in domain:
            return 'Reddit', 'fab fa-reddit', '#FF4500'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'Twitter/X', 'fab fa-twitter', '#1DA1F2'
        elif 'facebook.com' in domain or 'fb.com' in domain:
            return 'Facebook', 'fab fa-facebook', '#1877F2'
        elif 'threads.net' in domain:
            return 'Threads', 'fas fa-comments', '#000000'
        else:
            return '기타', 'fas fa-globe', '#6C757D'
    except:
        return '알 수 없음', 'fas fa-question', '#6C757D'

def normalize_reddit_url(url):
    """Reddit URL을 정규화합니다."""
    if 'reddit.com' in url and '/r/' in url:
        # www.reddit.com -> old.reddit.com 변환
        url = url.replace('www.reddit.com', 'old.reddit.com')
        # HTTPS 강제
        if not url.startswith('https://'):
            url = 'https://' + url.lstrip('http://')
    return url

def normalize_twitter_url(url):
    """Twitter/X URL을 정규화합니다."""
    # x.com을 twitter.com으로 변환
    url = url.replace('x.com', 'twitter.com')
    # HTTPS 강제
    if not url.startswith('https://'):
        url = 'https://' + url.lstrip('http://')
    return url

def normalize_facebook_url(url):
    """Facebook URL을 정규화합니다."""
    # m.facebook.com을 www.facebook.com으로 변환
    url = url.replace('m.facebook.com', 'www.facebook.com')
    # HTTPS 강제
    if not url.startswith('https://'):
        url = 'https://' + url.lstrip('http://')
    return url

def normalize_threads_url(url):
    """Threads URL을 정규화합니다."""
    # HTTPS 강제
    if not url.startswith('https://'):
        url = 'https://' + url.lstrip('http://')
    return url

def check_platform_availability():
    """각 플랫폼의 가용성을 체크합니다."""
    availability = {
        'YouTube': 'available',
        'TikTok': 'limited',
        'Instagram': 'limited',
        'Reddit': 'limited',
        'Twitter/X': 'limited'
    }
    return availability

def download_with_fallback(url, platform, outtmpl):
    """여러 방법으로 다운로드를 시도하는 함수"""
    import time
    import random
    
    print(f"🔄 서버 환경에서 {platform} 다운로드 시작: {url}", flush=True)
    logger.info(f"서버 환경에서 {platform} 다운로드 시작: {url}")
    
    # 방법 1: 최적화된 yt-dlp 설정
    try:
        print("⏳ 방법 1: 최적화된 yt-dlp 시도", flush=True)
        time.sleep(random.uniform(0.5, 1.5))
        opts = get_server_optimized_options(platform, outtmpl)
        logger.info("방법 1: 최적화된 yt-dlp 시도")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                print("📊 비디오 정보 추출 중...", flush=True)
                info = ydl.extract_info(url, download=False)
                if info and info.get('title'):
                    print(f"✅ 비디오 정보 확인됨: {info.get('title')}", flush=True)
                    logger.info(f"비디오 정보 확인됨: {info.get('title')}")
                    print("💾 다운로드 실행 중...", flush=True)
                    ydl.download([url])
                    print("✅ 방법 1 다운로드 완료!", flush=True)
                    return True
            except Exception as extract_error:
                print(f"⚠️ 정보 추출 실패, 직접 다운로드 시도: {str(extract_error)}", flush=True)
                logger.warning(f"정보 추출 실패, 직접 다운로드 시도: {str(extract_error)}")
                print("💾 직접 다운로드 시도 중...", flush=True)
                ydl.download([url])
                print("✅ 방법 1 직접 다운로드 완료!", flush=True)
                return True
    except Exception as e:
        print(f"❌ 방법 1 실패: {str(e)}", flush=True)
        logger.error(f"방법 1 실패: {str(e)}")
    
    # 방법 2: 간단한 설정으로 재시도
    try:
        print("⏳ 방법 2: 간단한 설정으로 시도", flush=True)
        time.sleep(random.uniform(1, 2))
        simple_opts = {
            'format': 'worst/best',
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'retries': 5,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'no_playlist': True
        }
        logger.info("방법 2: 간단한 설정으로 시도")
        
        with yt_dlp.YoutubeDL(simple_opts) as ydl:
            print("💾 방법 2 다운로드 실행 중...", flush=True)
            ydl.download([url])
        print("✅ 방법 2 다운로드 완료!", flush=True)
        return True
    except Exception as e:
        print(f"❌ 방법 2 실패: {str(e)}", flush=True)
        logger.error(f"방법 2 실패: {str(e)}")
    
    # 방법 3: YouTube의 경우 pytube 재시도
    if platform == 'YouTube':
        try:
            print("⏳ 방법 3: pytube로 YouTube 시도", flush=True)
            logger.info("방법 3: pytube로 YouTube 시도")
            time.sleep(random.uniform(1, 2))
            filename = download_youtube_with_pytube(url, outtmpl)
            if filename and os.path.exists(filename):
                print("✅ 방법 3 pytube 다운로드 완료!", flush=True)
                return True
        except Exception as e:
            print(f"❌ 방법 3 실패: {str(e)}", flush=True)
            logger.error(f"방법 3 실패: {str(e)}")
    
    print("❌ 모든 다운로드 방법 실패", flush=True)
    return False

# HTML 템플릿
HTML_FORM = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 마케팅 김이사가 만든 다운로드 서비스</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
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
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
            text-align: center;
        }

        .title {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.2em;
            font-weight: bold;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .form-group {
            margin-bottom: 25px;
            text-align: left;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }

        input[type="url"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #fff;
        }

        input[type="url"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 10px;
        }

        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }

        .alert {
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: 500;
        }

        .alert-error {
            background-color: rgba(220, 53, 69, 0.1);
            border: 1px solid rgba(220, 53, 69, 0.3);
            color: #721c24;
        }

        .alert-success {
            background-color: rgba(25, 135, 84, 0.1);
            border: 1px solid rgba(25, 135, 84, 0.3);
            color: #0f5132;
        }

        .platform-info {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
        }

        .platform-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .youtube { background: rgba(255, 0, 0, 0.1); color: #d73502; }
        .tiktok { background: rgba(0, 0, 0, 0.1); color: #000; }
        .instagram { background: rgba(228, 64, 95, 0.1); color: #e4405f; }
        .twitter { background: rgba(29, 161, 242, 0.1); color: #1da1f2; }
        .reddit { background: rgba(255, 69, 0, 0.1); color: #ff4500; }
        .facebook { background: rgba(24, 119, 242, 0.1); color: #1877f2; }

        .download-link {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 15px;
            transition: all 0.3s ease;
        }

        .download-link:hover {
            background: #218838;
            transform: translateY(-2px);
        }

        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }
            
            .title {
                font-size: 1.8em;
            }
            
            .platform-info {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">🔥 비디오 다운로더</h1>
        <p class="subtitle">마케팅 김이사가 만든 소셜 미디어 다운로드 서비스</p>
        
        <div class="platform-info">
            <div class="platform-badge youtube">
                <i class="fab fa-youtube"></i> YouTube
            </div>
            <div class="platform-badge tiktok">
                <i class="fab fa-tiktok"></i> TikTok
            </div>
            <div class="platform-badge instagram">
                <i class="fab fa-instagram"></i> Instagram
            </div>
            <div class="platform-badge twitter">
                <i class="fab fa-twitter"></i> Twitter
            </div>
            <div class="platform-badge reddit">
                <i class="fab fa-reddit"></i> Reddit
            </div>
            <div class="platform-badge facebook">
                <i class="fab fa-facebook"></i> Facebook
            </div>
        </div>

        <form method="POST">
            <div class="form-group">
                <label for="url">
                    <i class="fas fa-link"></i> 비디오 URL 입력
                </label>
                <input type="url" 
                       id="url" 
                       name="url" 
                       placeholder="https://youtube.com/watch?v=..." 
                       required
                       value="{{ request.form.url if request.form.url else '' }}">
            </div>
            
            <button type="submit" class="submit-btn">
                <i class="fas fa-download"></i> 다운로드 시작
            </button>
        </form>

        {% if error %}
        <div class="alert alert-error">
            <i class="fas fa-exclamation-triangle"></i> {{ error }}
        </div>
        {% endif %}

        {% if success %}
        <div class="alert alert-success">
            <i class="fas fa-check-circle"></i> {{ success }}
            {% if filename %}
            <br><br>
            <a href="/file/{{ filename }}" class="download-link">
                <i class="fas fa-download"></i> 파일 다운로드
            </a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    print("🏠 메인 페이지 접속", flush=True)
    return render_template_string(HTML_FORM)

@app.route('/', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()
    
    print(f"📥 다운로드 요청 받음: {url}", flush=True)
    logger.info(f"다운로드 요청: {url}")
    
    if not url:
        print("❌ URL이 비어있음", flush=True)
        return render_template_string(HTML_FORM, error="URL을 입력하세요.")
    
    # 플랫폼 감지
    platform, icon, color = detect_platform(url)
    print(f"🎯 감지된 플랫폼: {platform}", flush=True)
    logger.info(f"감지된 플랫폼: {platform}")
    
    # Reddit URL 정규화
    if platform == 'Reddit':
        original_url = url
        url = normalize_reddit_url(url)
        print(f"🔗 Reddit URL 정규화: {original_url} -> {url}", flush=True)
        logger.info(f"Reddit URL 정규화: {original_url} -> {url}")
    
    # Twitter/X URL 정규화
    if platform == 'Twitter/X':
        original_url = url
        url = normalize_twitter_url(url)
        print(f"🔗 Twitter/X URL 정규화: {original_url} -> {url}", flush=True)
        logger.info(f"Twitter/X URL 정규화: {original_url} -> {url}")
    
    # Facebook URL 정규화
    if platform == 'Facebook':
        original_url = url
        url = normalize_facebook_url(url)
        print(f"🔗 Facebook URL 정규화: {original_url} -> {url}", flush=True)
        logger.info(f"Facebook URL 정규화: {original_url} -> {url}")
    
    # Threads URL 정규화
    if platform == 'Threads':
        original_url = url
        url = normalize_threads_url(url)
        print(f"🔗 Threads URL 정규화: {original_url} -> {url}", flush=True)
        logger.info(f"Threads URL 정규화: {original_url} -> {url}")
    
    # 고유 파일명 생성
    unique_id = str(uuid.uuid4())
    outtmpl = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.%(ext)s")
    print(f"📁 생성된 파일 템플릿: {outtmpl}", flush=True)
    
    try:
        print(f"🚀 다운로드 프로세스 시작: {url} (플랫폼: {platform})", flush=True)
        logger.info(f"다운로드 시작: {url} (플랫폼: {platform})")
        
        # YouTube 특별 처리
        if platform == 'YouTube':
            try:
                print("📺 YouTube 감지 - pytube 먼저 시도", flush=True)
                # 먼저 pytube로 시도
                filename = download_youtube_with_pytube(url, outtmpl)
                if filename and os.path.exists(filename):
                    base = os.path.basename(filename)
                    print(f"✅ pytube로 다운로드 완료: {base}", flush=True)
                    logger.info(f"pytube로 다운로드 완료: {base}")
                    return send_file(filename, as_attachment=True, download_name=base)
            except Exception as pytube_error:
                print(f"❌ pytube 실패: {str(pytube_error)}", flush=True)
                logger.error(f"pytube 실패: {str(pytube_error)}")
                
                # yt-dlp로 재시도
                try:
                    print("🔄 yt-dlp로 재시도", flush=True)
                    ydl_opts = get_server_optimized_options(platform, outtmpl)
                    logger.info("yt-dlp로 YouTube 다운로드 시도...")
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        print("💾 yt-dlp 다운로드 실행...", flush=True)
                        ydl.download([url])
                        
                except Exception as ydl_error:
                    print(f"❌ yt-dlp도 실패: {str(ydl_error)}", flush=True)
                    error_str = str(ydl_error).lower()
                    if 'sign in' in error_str or 'bot' in error_str:
                        return render_template_string(HTML_FORM, 
                                                    error="YouTube가 봇 차단을 적용했습니다. 다시 시도해주세요.")
                    else:
                        raise Exception(f"YouTube 다운로드 실패: {str(ydl_error)}")
        
        # 기타 플랫폼 처리
        else:
            print(f"🔧 기타 플랫폼 처리: {platform}", flush=True)
            success = download_with_fallback(url, platform, outtmpl)
            if not success:
                print(f"❌ {platform} 다운로드 실패", flush=True)
                return render_template_string(HTML_FORM, 
                                            error=f"{platform} 다운로드에 실패했습니다. 다시 시도해주세요.")
        
        # 다운로드된 파일 찾기 - 더 자세한 추적
        print("🔍 다운로드된 파일 검색 중...", flush=True)
        print(f"📁 검색 대상 폴더: {DOWNLOAD_FOLDER}", flush=True)
        
        # 폴더 내 모든 파일 나열
        try:
            all_files = os.listdir(DOWNLOAD_FOLDER)
            print(f"📂 폴더 내 모든 파일: {all_files}", flush=True)
        except Exception as e:
            print(f"❌ 폴더 읽기 실패: {e}", flush=True)
            return render_template_string(HTML_FORM, 
                                        error=f"다운로드 폴더 접근 실패: {str(e)}")
        
        # 비디오/오디오 파일만 필터링
        video_extensions = ('.mp4', '.webm', '.mkv', '.m4a', '.mp3', '.wav', '.avi', '.mov')
        files = [f for f in all_files if f.lower().endswith(video_extensions)]
        print(f"🎵 비디오/오디오 파일들: {files}", flush=True)
        
        # unique_id가 포함된 파일들도 확인
        unique_files = [f for f in all_files if unique_id in f]
        print(f"🔑 ID가 포함된 파일들: {unique_files}", flush=True)
        
        if files:
            # 가장 최근 파일 선택
            files.sort(key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_FOLDER, x)), reverse=True)
            filename = os.path.join(DOWNLOAD_FOLDER, files[0])
            base = os.path.basename(filename)
            print(f"🎉 다운로드 완료: {base}", flush=True)
            logger.info(f"다운로드 완료: {base}")
            
            # 파일 크기 확인
            file_size = os.path.getsize(filename)
            print(f"📊 파일 크기: {file_size} bytes", flush=True)
            
            # 파일이 유효한지 확인 (크기가 0이 아닌지)
            if file_size > 0:
                print("✅ 유효한 파일 확인됨", flush=True)
                return send_file(filename, as_attachment=True, download_name=base)
            else:
                print("❌ 파일 크기가 0 - 다운로드 실패", flush=True)
                return render_template_string(HTML_FORM, 
                                            error="다운로드된 파일이 비어있습니다. 다시 시도해주세요.")
        else:
            print("❌ 다운로드된 파일을 찾을 수 없음", flush=True)
            print(f"🔍 검색한 확장자: {video_extensions}", flush=True)
            return render_template_string(HTML_FORM, 
                                        error="다운로드된 파일을 찾을 수 없습니다. 다시 시도해주세요.")
        
    except Exception as e:
        error_msg = f"다운로드 실패: {str(e)}"
        print(f"💥 예외 발생: {error_msg}", flush=True)
        logger.error(error_msg)
        return render_template_string(HTML_FORM, error=error_msg)

@app.route('/file/<filename>')
def file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    print(f"📁 파일 요청: {filename}, 경로: {path}", flush=True)
    if os.path.exists(path):
        print(f"✅ 파일 존재 확인, 전송 시작", flush=True)
        return send_file(path, as_attachment=True)
    else:
        print(f"❌ 파일이 존재하지 않음: {path}", flush=True)
        return "파일을 찾을 수 없습니다.", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    host = '0.0.0.0' if IS_SERVER_ENV else 'localhost'
    
    print(f"🚀 Flask 앱 시작!", flush=True)
    print(f"📍 주소: http://{host}:{port}", flush=True)
    print(f"🌐 서버 환경: {'예' if IS_SERVER_ENV else '아니오'}", flush=True)
    print(f"📁 다운로드 폴더: {DOWNLOAD_FOLDER}", flush=True)
    print(f"🍪 쿠키 파일: {fake_cookies}", flush=True)
    
    app.run(host=host, port=port, debug=not IS_SERVER_ENV) 