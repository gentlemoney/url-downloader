from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import uuid
import logging
import re

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 다운로드 폴더 설정
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def normalize_reddit_url(url):
    """Reddit URL을 정규화합니다."""
    import re
    
    # Reddit URL 패턴들
    patterns = [
        r'https?://(?:www\.)?reddit\.com/r/[^/]+/comments/[^/]+/[^/]+/?',
        r'https?://(?:www\.)?reddit\.com/r/[^/]+/comments/[^/]+/?',
        r'https?://v\.redd\.it/[^/]+',
        r'https?://(?:www\.)?reddit\.com/gallery/[^/]+',
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            # URL 끝의 슬래시 제거
            url = url.rstrip('/')
            return url
    
    return url

def normalize_twitter_url(url):
    """Twitter/X URL을 정규화합니다."""
    import re
    
    # Twitter/X URL 패턴들
    patterns = [
        r'https?://(?:www\.)?twitter\.com/[^/]+/status/\d+',
        r'https?://(?:www\.)?x\.com/[^/]+/status/\d+',
        r'https?://(?:www\.)?twitter\.com/i/status/\d+',
        r'https?://(?:www\.)?x\.com/i/status/\d+',
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            # URL 끝의 슬래시 제거
            url = url.rstrip('/')
            return url
    
    return url

def detect_platform(url):
    """URL에서 플랫폼을 감지합니다."""
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube', 'fab fa-youtube', '#FF0000'
    elif 'tiktok.com' in url_lower:
        return 'TikTok', 'fab fa-tiktok', '#000000'
    elif 'instagram.com' in url_lower or 'instagr.am' in url_lower:
        return 'Instagram', 'fab fa-instagram', '#E4405F'
    elif 'reddit.com' in url_lower or 'redd.it' in url_lower:
        # Reddit URL 정규화
        if '/comments/' in url_lower:
            return 'Reddit', 'fab fa-reddit', '#FF4500'
        else:
            return 'Reddit', 'fab fa-reddit', '#FF4500'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'Twitter/X', 'fab fa-twitter', '#1DA1F2'
    else:
        return 'Unknown', 'fas fa-video', '#666666'

def get_platform_specific_options(platform):
    """플랫폼별 최적화된 다운로드 옵션을 반환합니다."""
    base_options = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'ignoreerrors': False,
        'nocheckcertificate': True,
        'extractor_retries': 3,
    }
    
    if platform == 'TikTok':
        base_options.update({
            'format': 'best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'cookiesfrombrowser': ('chrome',),  # TikTok은 쿠키가 필요할 수 있음
        })
    elif platform == 'Instagram':
        base_options.update({
            'format': 'best[ext=mp4]/best[height<=1080]/best',
            'merge_output_format': 'mp4',
            'cookiesfrombrowser': ('chrome',),  # Instagram은 로그인 필요할 수 있음
            'extract_flat': False,
            'ignoreerrors': True,  # Instagram은 일부 콘텐츠에 접근 제한이 있을 수 있음
            'extractor_retries': 5,  # Instagram은 재시도가 필요할 수 있음
        })
    elif platform == 'Reddit':
        base_options.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'extract_flat': False,
            'ignoreerrors': True,
            'extractor_retries': 5,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'cookiesfrombrowser': ('chrome',),
            'nocheckcertificate': True,
            'no_warnings': False,
            'quiet': False,
            'extractaudio': False,
            'audioformat': 'mp3',
            'audioquality': '0',
            'recodevideo': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'prefer_ffmpeg': True,
            'keepvideo': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'subtitleslangs': ['en'],
            'skip_download': False,
            'outtmpl': '%(title)s.%(ext)s',
        })
    elif platform == 'Twitter/X':
        base_options.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'cookiesfrombrowser': ('chrome',),
            'extract_flat': False,
            'ignoreerrors': True,
            'extractor_retries': 5,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'nocheckcertificate': True,
            'no_warnings': False,
            'quiet': False,
            'extractaudio': False,
            'audioformat': 'mp3',
            'audioquality': '0',
            'recodevideo': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'prefer_ffmpeg': True,
            'keepvideo': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'subtitleslangs': ['en'],
            'skip_download': False,
            'outtmpl': '%(title)s.%(ext)s',
        })
    else:  # YouTube 및 기타
        base_options.update({
            'format': 'best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        })
    
    return base_options

# HTML 템플릿
HTML_FORM = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>소셜 미디어 다운로드</title>
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
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        
        .header {
            margin-bottom: 30px;
        }
        
        .header i {
            font-size: 3em;
            color: #FF0000;
            margin-bottom: 10px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.2em;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 30px;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        button:hover {
            transform: translateY(-2px);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .platform-info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: left;
        }
        
        .platform-item {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin: 5px 10px 5px 0;
            padding: 8px 12px;
            background: white;
            border-radius: 20px;
            font-size: 0.9em;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .platform-item i {
            font-size: 1.2em;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #f5c6cb;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #c3e6cb;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .download-link {
            display: inline-block;
            background: #28a745;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            margin-top: 10px;
            transition: background-color 0.3s ease;
        }
        
        .download-link:hover {
            background: #218838;
        }
        
        .loading {
            display: none;
            margin-top: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .tips {
            margin-top: 20px;
            font-size: 0.9em;
            color: #666;
        }
        
        .tips h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .tips ul {
            text-align: left;
            list-style-type: none;
            padding-left: 0;
        }
        
        .tips li {
            margin-bottom: 5px;
            padding-left: 20px;
            position: relative;
        }
        
        .tips li:before {
            content: "✓";
            color: #28a745;
            font-weight: bold;
            position: absolute;
            left: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <i class="fas fa-download"></i>
            <h1>소셜 미디어 다운로드</h1>
            <p class="subtitle">YouTube, TikTok, Instagram 등 다양한 플랫폼의 영상을 다운로드하세요</p>
        </div>
        
        <div class="platform-info">
            <h3>지원 플랫폼:</h3>
            <div class="platform-item">
                <i class="fab fa-youtube" style="color: #FF0000;"></i>
                <span>YouTube</span>
                <small style="color: #666; font-size: 0.8em;">(영상, 음악)</small>
            </div>
            <div class="platform-item">
                <i class="fab fa-tiktok" style="color: #000000;"></i>
                <span>TikTok</span>
                <small style="color: #666; font-size: 0.8em;">(비디오)</small>
            </div>
            <div class="platform-item">
                <i class="fab fa-instagram" style="color: #E4405F;"></i>
                <span>Instagram</span>
                <small style="color: #666; font-size: 0.8em;">(Reels, Posts)</small>
            </div>
            <div class="platform-item">
                <i class="fab fa-reddit" style="color: #FF4500;"></i>
                <span>Reddit</span>
                <small style="color: #666; font-size: 0.8em;">(Videos, GIFs)</small>
            </div>
            <div class="platform-item">
                <i class="fab fa-twitter" style="color: #1DA1F2;"></i>
                <span>Twitter/X</span>
                <small style="color: #666; font-size: 0.8em;">(Videos)</small>
            </div>
        </div>
        
        <form method="POST" action="/download" id="downloadForm">
            <div class="input-group">
                <input type="text" name="url" placeholder="영상 링크를 입력하세요 (YouTube, TikTok, Instagram 등)" required>
                <button type="submit" id="downloadBtn">
                    <i class="fas fa-download"></i>
                    다운로드
                </button>
            </div>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>다운로드 중...</p>
        </div>
        
        {% if error %}
        <div class="error">
            <i class="fas fa-exclamation-triangle"></i>
            {{ error }}
        </div>
        {% endif %}
        
        {% if filename %}
        <div class="success">
            <i class="fas fa-check-circle"></i>
            다운로드 완료!
            <br>
            <a href="/file/{{ filename }}" class="download-link" download>
                <i class="fas fa-download"></i>
                파일 다운로드
            </a>
        </div>
        {% endif %}
        
        <div class="tips">
            <h3>사용 팁:</h3>
            <ul>
                <li>공개 영상만 다운로드 가능합니다</li>
                <li>일부 플랫폼은 로그인이 필요할 수 있습니다</li>
                <li>저작권에 유의하여 사용하세요</li>
                <li>다운로드된 파일은 자동으로 삭제됩니다</li>
            </ul>
        </div>
    </div>
    
    <script>
        document.getElementById('downloadForm').addEventListener('submit', function() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('downloadBtn').disabled = true;
        });
        
        // URL 입력 시 플랫폼 감지
        document.querySelector('input[name="url"]').addEventListener('input', function() {
            const url = this.value.toLowerCase();
            let platform = 'Unknown';
            let icon = 'fas fa-video';
            let color = '#666666';
            
            if (url.includes('youtube.com') || url.includes('youtu.be')) {
                platform = 'YouTube';
                icon = 'fab fa-youtube';
                color = '#FF0000';
            } else if (url.includes('tiktok.com')) {
                platform = 'TikTok';
                icon = 'fab fa-tiktok';
                color = '#000000';
            } else if (url.includes('instagram.com') || url.includes('instagr.am')) {
                platform = 'Instagram';
                icon = 'fab fa-instagram';
                color = '#E4405F';
            } else if (url.includes('reddit.com') || url.includes('redd.it')) {
                platform = 'Reddit';
                icon = 'fab fa-reddit';
                color = '#FF4500';
            } else if (url.includes('twitter.com') || url.includes('x.com')) {
                platform = 'Twitter/X';
                icon = 'fab fa-twitter';
                color = '#1DA1F2';
            }
            
            // 플랫폼 정보 업데이트 (선택사항)
            console.log('감지된 플랫폼:', platform);
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_FORM)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return render_template_string(HTML_FORM, error="URL을 입력하세요.")
    
    # 플랫폼 감지
    platform, icon, color = detect_platform(url)
    logger.info(f"감지된 플랫폼: {platform}")
    
    # Reddit URL 정규화
    if platform == 'Reddit':
        original_url = url
        url = normalize_reddit_url(url)
        logger.info(f"Reddit URL 정규화: {original_url} -> {url}")
    
    # Twitter/X URL 정규화
    if platform == 'Twitter/X':
        original_url = url
        url = normalize_twitter_url(url)
        logger.info(f"Twitter/X URL 정규화: {original_url} -> {url}")
    
    # 고유 파일명 생성
    outtmpl = os.path.join(DOWNLOAD_FOLDER, f"{uuid.uuid4()}.%(ext)s")
    
    # 플랫폼별 최적화된 옵션 가져오기
    ydl_opts = get_platform_specific_options(platform)
    ydl_opts['outtmpl'] = outtmpl
    
    try:
        logger.info(f"다운로드 시작: {url} (플랫폼: {platform})")
        logger.info(f"yt-dlp 옵션: {ydl_opts}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 먼저 정보만 추출해서 영상이 접근 가능한지 확인
            try:
                logger.info("영상 정보 추출 시작...")
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("영상 정보를 가져올 수 없습니다. 링크를 확인해주세요.")
                
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 'Unknown')
                logger.info(f"영상 제목: {title}, 길이: {duration}초")
                
                # 실제 다운로드 실행
                logger.info("실제 다운로드 시작...")
                ydl.download([url])
                
                # 다운로드된 파일 찾기
                filename = ydl.prepare_filename(info)
                if not filename or not os.path.exists(filename):
                    # UUID 기반 파일명으로 대체
                    filename = os.path.join(DOWNLOAD_FOLDER, f"{uuid.uuid4()}.mp4")
                
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename)[0] + '.mp4'
                
                base = os.path.basename(filename)
                logger.info(f"다운로드 완료: {base}")
                
            except Exception as extract_error:
                logger.error(f"영상 정보 추출 실패: {str(extract_error)}")
                raise Exception(f"영상 정보를 가져올 수 없습니다: {str(extract_error)}")
            
        return render_template_string(HTML_FORM, filename=base)
        
    except Exception as e:
        error_msg = f"다운로드 실패: {str(e)}"
        logger.error(error_msg)
        return render_template_string(HTML_FORM, error=error_msg)

@app.route('/file/<filename>')
def file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "파일을 찾을 수 없습니다.", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000) 