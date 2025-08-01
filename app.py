from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import uuid
import logging
import re
import requests
import json

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 임시 저장 폴더
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

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
            return 'Reddit', 'fab fa-reddit', '#FF4500'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'Twitter/X', 'fab fa-twitter', '#1DA1F2'
    elif 'threads.net' in url_lower:
        return 'Threads', 'fab fa-threads', '#000000'
    else:
        return 'Unknown', 'fas fa-video', '#666666'

def get_platform_specific_options(platform):
    """플랫폼별 최적화된 다운로드 옵션을 반환합니다."""
    # Render 환경 확인 (더 정확한 감지)
    is_render = (
        os.environ.get('RENDER') == 'true' or 
        os.environ.get('RENDER_SERVICE_NAME') is not None or
        'onrender.com' in os.environ.get('HOSTNAME', '')
    )
    
    base_options = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'ignoreerrors': False,
        'nocheckcertificate': True,
        'extractor_retries': 3,
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'http_chunk_size': 10485760,  # 10MB chunks
    }
    
    if platform == 'TikTok':
        base_options.update({
            'format': 'best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        })
        if not is_render:
            base_options['cookiesfrombrowser'] = ('chrome',)
    elif platform == 'Instagram':
        base_options.update({
            'format': 'best[ext=mp4]/best[height<=1080]/best',
            'merge_output_format': 'mp4',
            'extract_flat': False,
            'ignoreerrors': True,
            'extractor_retries': 5,
        })
        if not is_render:
            base_options['cookiesfrombrowser'] = ('chrome',)
    elif platform == 'Reddit':
        base_options.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
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
        if not is_render:
            base_options['cookiesfrombrowser'] = ('chrome',)
    elif platform == 'Twitter/X':
        base_options.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
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
        if not is_render:
            base_options['cookiesfrombrowser'] = ('chrome',)
    elif platform == 'Threads':
        # Threads는 Instagram 계열이므로 유사한 설정 사용
        base_options.update({
            'format': 'best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'extract_flat': False,
            'ignoreerrors': True,
            'extractor_retries': 5,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'nocheckcertificate': True,
            'no_warnings': False,
            'quiet': False,
        })
        if not is_render:
            base_options['cookiesfrombrowser'] = ('chrome',)
    else:  # YouTube 및 기타
        base_options.update({
            'format': 'best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            },
            'age_limit': None,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'prefer_free_formats': True,
        })
        
        # YouTube 특별 처리
        if 'youtube' in platform.lower():
            base_options.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'youtube_include_dash_manifest': False,
                'youtube_include_hls_manifest': False,
                'no_check_certificates': True,
                'cookiesfrombrowser': None,  # Render에서는 브라우저 쿠키 사용 불가
                'use_extractors': ['youtube:tab', 'youtube'],
            })
    
    return base_options

HTML_FORM = '''
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>소셜 미디어 다운로드 - gptkimisa.com</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
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
        max-width: 700px;
        width: 100%;
        text-align: center;
      }
      
      .logo {
        font-size: 2.5em;
        color: #ff0000;
        margin-bottom: 10px;
      }
      
      h1 {
        color: #333;
        margin-bottom: 10px;
        font-size: 2em;
        font-weight: 300;
      }
      
      .subtitle {
        color: #666;
        margin-bottom: 30px;
        font-size: 1.1em;
      }
      
      .platform-info {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        display: none;
      }
      
      .platform-info.show {
        display: block;
      }
      
      .platform-icon {
        font-size: 1.5em;
        margin-right: 10px;
      }
      
      .form-group {
        margin-bottom: 20px;
      }
      
      .input-group {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
      }
      
      input[type="text"] {
        flex: 1;
        padding: 15px 20px;
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        font-size: 16px;
        transition: all 0.3s ease;
        outline: none;
      }
      
      input[type="text"]:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
      
      button {
        padding: 15px 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      
      button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
      }
      
      button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }
      
      .error {
        background: #fee;
        color: #c33;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        border-left: 4px solid #c33;
      }
      
      .success {
        background: #efe;
        color: #363;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        border-left: 4px solid #363;
      }
      
      .download-link {
        display: inline-block;
        background: #28a745;
        color: white;
        padding: 12px 25px;
        text-decoration: none;
        border-radius: 8px;
        margin-top: 10px;
        transition: all 0.3s ease;
      }
      
      .download-link:hover {
        background: #218838;
        transform: translateY(-1px);
      }
      
      .features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 20px;
        margin-top: 30px;
        padding-top: 30px;
        border-top: 1px solid #eee;
      }
      
      .feature {
        text-align: center;
        padding: 20px;
      }
      
      .feature i {
        font-size: 2em;
        color: #667eea;
        margin-bottom: 10px;
      }
      
      .feature h3 {
        color: #333;
        margin-bottom: 5px;
        font-size: 1.1em;
      }
      
      .feature p {
        color: #666;
        font-size: 0.9em;
      }
      
      .supported-platforms {
        margin-top: 20px;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 10px;
      }
      
      .platform-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 15px;
        margin-top: 15px;
      }
      
      .platform-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px;
        border-radius: 5px;
        background: white;
        font-size: 0.9em;
      }
      
      .loading {
        display: none;
        margin-top: 20px;
      }
      
      .spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 0 auto 10px;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      @media (max-width: 768px) {
        .container {
          padding: 20px;
          margin: 10px;
        }
        
        .input-group {
          flex-direction: column;
        }
        
        h1 {
          font-size: 1.5em;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="logo">
        <i class="fas fa-download"></i>
      </div>
      <h1>소셜 미디어 다운로드</h1>
      <p class="subtitle">YouTube, TikTok, Instagram 등 다양한 플랫폼의 영상을 다운로드하세요</p>
      
      <div class="platform-info" id="platformInfo">
        <i class="platform-icon" id="platformIcon"></i>
        <span id="platformName">플랫폼을 감지했습니다</span>
      </div>
      
      <form method="post" action="/" id="downloadForm">
        <div class="form-group">
          <div class="input-group">
            <input type="text" name="url" placeholder="영상 링크를 입력하세요 (YouTube, TikTok, Instagram 등)" required id="urlInput">
            <button type="submit" id="downloadBtn">
              <i class="fas fa-download"></i>
              다운로드
            </button>
          </div>
        </div>
      </form>
      
      <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>다운로드 중입니다...</p>
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
          다운로드가 완료되었습니다!
          <br>
          <a href="/file/{{ filename }}" class="download-link">
            <i class="fas fa-download"></i>
            파일 다운로드
          </a>
        </div>
      {% endif %}
      
      <div class="supported-platforms">
        <h3>지원하는 플랫폼</h3>
        <div class="platform-grid">
          <div class="platform-item">
            <i class="fab fa-youtube" style="color: #FF0000;"></i>
            <span>YouTube</span>
          </div>
          <div class="platform-item">
            <i class="fab fa-tiktok" style="color: #000000;"></i>
            <span>TikTok</span>
          </div>
          <div class="platform-item">
            <i class="fab fa-instagram" style="color: #E4405F;"></i>
            <span>Instagram</span>
          </div>
          <div class="platform-item">
            <i class="fab fa-reddit" style="color: #FF4500;"></i>
            <span>Reddit</span>
          </div>
          <div class="platform-item">
            <i class="fab fa-twitter" style="color: #1DA1F2;"></i>
            <span>Twitter/X</span>
          </div>
          <div class="platform-item">
            <i class="fab fa-threads" style="color: #000000;"></i>
            <span>Threads</span>
          </div>
        </div>
        <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 5px; font-size: 0.9em; color: #856404;">
          <i class="fas fa-info-circle"></i>
          <strong>Instagram 팁:</strong> Reels, Stories, Posts 비디오를 지원합니다. 일부 콘텐츠는 로그인이 필요할 수 있습니다.
        </div>
        <div style="margin-top: 10px; padding: 10px; background: #f8d7da; border-radius: 5px; font-size: 0.9em; color: #721c24;">
          <i class="fas fa-exclamation-triangle"></i>
          <strong>YouTube 주의:</strong> 서버 환경에서는 봇 감지로 인해 일부 영상이 다운로드되지 않을 수 있습니다. 이 경우 로컬에서 시도해주세요.
        </div>
      </div>
      
      <div class="features">
        <div class="feature">
          <i class="fas fa-bolt"></i>
          <h3>빠른 다운로드</h3>
          <p>고속 서버로 빠른 다운로드</p>
        </div>
        <div class="feature">
          <i class="fas fa-shield-alt"></i>
          <h3>안전한 서비스</h3>
          <p>개인정보 보호 및 안전한 다운로드</p>
        </div>
        <div class="feature">
          <i class="fas fa-mobile-alt"></i>
          <h3>모바일 친화적</h3>
          <p>모든 기기에서 편리하게 사용</p>
        </div>
      </div>
    </div>
    
    <script>
      document.getElementById('urlInput').addEventListener('input', function() {
        const url = this.value;
        if (url) {
          const urlLower = url.toLowerCase();
          let platform = 'Unknown';
          let icon = 'fas fa-video';
          let color = '#666666';
          
          if (urlLower.includes('youtube.com') || urlLower.includes('youtu.be')) {
            platform = 'YouTube';
            icon = 'fab fa-youtube';
            color = '#FF0000';
          } else if (urlLower.includes('tiktok.com')) {
            platform = 'TikTok';
            icon = 'fab fa-tiktok';
            color = '#000000';
          } else if (urlLower.includes('instagram.com') || urlLower.includes('instagr.am')) {
            platform = 'Instagram';
            icon = 'fab fa-instagram';
            color = '#E4405F';
          } else if (urlLower.includes('reddit.com') || urlLower.includes('redd.it')) {
            platform = 'Reddit';
            icon = 'fab fa-reddit';
            color = '#FF4500';
          } else if (urlLower.includes('twitter.com') || urlLower.includes('x.com')) {
            platform = 'Twitter/X';
            icon = 'fab fa-twitter';
            color = '#1DA1F2';
          } else if (urlLower.includes('threads.net')) {
            platform = 'Threads';
            icon = 'fab fa-threads';
            color = '#000000';
          }
          
          document.getElementById('platformName').textContent = platform;
          document.getElementById('platformIcon').className = icon;
          document.getElementById('platformIcon').style.color = color;
          document.getElementById('platformInfo').classList.add('show');
        } else {
          document.getElementById('platformInfo').classList.remove('show');
        }
      });
      
      document.getElementById('downloadForm').addEventListener('submit', function() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('downloadBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> 처리중...';
      });
    </script>
  </body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return download()
    return render_template_string(HTML_FORM)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return render_template_string(HTML_FORM, error="URL을 입력하세요.")
    
    # 플랫폼 감지
    platform, icon, color = detect_platform(url)
    logger.info(f"감지된 플랫폼: {platform}")
    
    # 고유 파일명 생성
    outtmpl = os.path.join(DOWNLOAD_FOLDER, f"{uuid.uuid4()}.%(ext)s")
    
    # 플랫폼별 최적화된 옵션 가져오기
    ydl_opts = get_platform_specific_options(platform)
    ydl_opts['outtmpl'] = outtmpl
    
    try:
        logger.info(f"다운로드 시작: {url} (플랫폼: {platform})")
        
        # YouTube의 경우 추가 시도
        if 'youtube' in platform.lower() and (os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_NAME')):
            logger.info("Render 환경에서 YouTube 다운로드 - 특별 설정 적용")
            ydl_opts.update({
                'no_check_certificates': True,
                'prefer_insecure': True,
                'geo_verification_proxy': None,
                'source_address': '0.0.0.0',
            })
        
        download_success = False
        filename = None
        base = None
        
        # 첫 번째 시도
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("영상 정보 추출 시작...")
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("영상 정보를 가져올 수 없습니다.")
                
                title = info.get('title', 'Unknown')
                logger.info(f"영상 제목: {title}")
                
                # 실제 다운로드 실행
                logger.info("실제 다운로드 시작...")
                ydl.download([url])
                
                # 다운로드된 파일 찾기
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename)[0] + '.mp4'
                    
                if os.path.exists(filename):
                    base = os.path.basename(filename)
                    download_success = True
                    logger.info(f"다운로드 완료: {base}")
                    
        except Exception as e:
            logger.error(f"첫 번째 시도 실패: {str(e)}")
            
            # YouTube의 경우 여러 방법으로 재시도
            if 'youtube' in platform.lower():
                logger.info("YouTube 다운로드 재시도 - 봇 감지 우회 설정")
                
                # 방법 1: 모바일 User-Agent 사용
                mobile_opts = {
                    'format': 'best',
                    'outtmpl': outtmpl,
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-us',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                            'player_skip': ['webpage', 'config'],
                        }
                    },
                }
                
                try:
                    with yt_dlp.YoutubeDL(mobile_opts) as ydl:
                        ydl.download([url])
                        
                        # 다운로드된 파일 찾기
                        for file in os.listdir(DOWNLOAD_FOLDER):
                            if file.startswith(os.path.basename(outtmpl).split('.')[0]):
                                filename = os.path.join(DOWNLOAD_FOLDER, file)
                                base = file
                                download_success = True
                                logger.info(f"모바일 UA로 다운로드 성공: {base}")
                                break
                                
                except Exception as mobile_error:
                    logger.error(f"모바일 UA 시도 실패: {str(mobile_error)}")
                    
                    # 방법 2: 임베드 페이지 사용
                    if not download_success:
                        logger.info("YouTube 다운로드 재시도 - 임베드 방식")
                        embed_opts = {
                            'format': 'best',
                            'outtmpl': outtmpl,
                            'quiet': False,
                            'force_generic_extractor': False,
                            'extractor_args': {
                                'youtube': {
                                    'player_client': ['web_embedded'],
                                }
                            },
                        }
                        
                        try:
                            with yt_dlp.YoutubeDL(embed_opts) as ydl:
                                ydl.download([url])
                                
                                for file in os.listdir(DOWNLOAD_FOLDER):
                                    if file.startswith(os.path.basename(outtmpl).split('.')[0]):
                                        filename = os.path.join(DOWNLOAD_FOLDER, file)
                                        base = file
                                        download_success = True
                                        logger.info(f"임베드 방식으로 다운로드 성공: {base}")
                                        break
                                        
                        except Exception as embed_error:
                            logger.error(f"임베드 방식도 실패: {str(embed_error)}")
        
        if download_success and base:
            return render_template_string(HTML_FORM, filename=base)
        else:
            raise Exception("다운로드를 완료할 수 없습니다.")
        
    except Exception as e:
        error_msg = f"다운로드 실패: {str(e)}"
        logger.error(error_msg)
        return render_template_string(HTML_FORM, error=error_msg)

@app.route('/file/<filename>')
def file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "파일이 존재하지 않습니다.", 404

if __name__ == '__main__':
    # Render 환경 자동 감지
    if os.environ.get('RENDER'):
        os.environ['RENDER'] = 'true'
        print("🚀 Render 환경에서 실행 중...")
    
    # 로컬: 0.0.0.0:3000, Render: PORT 환경변수 사용
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug_mode = False if os.environ.get('RENDER') else True
    
    app.run(debug=debug_mode, host=host, port=port) 