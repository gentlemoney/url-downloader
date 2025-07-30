from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import uuid
import logging
import re
import requests
import json

app = Flask(__name__)

# 로깅 설정 - 최소화
logging.basicConfig(level=logging.WARNING)
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
    else:
        return 'Unknown', 'fas fa-video', '#666666'

def get_platform_specific_options(platform):
    """플랫폼별 최적화된 다운로드 옵션을 반환합니다."""
    base_options = {
        'quiet': True,  # 더 조용하게
        'no_warnings': True,  # 경고 메시지 숨김
        'extract_flat': False,
        'ignoreerrors': False,
        'nocheckcertificate': True,
        'extractor_retries': 3,
    }
    
    if platform == 'TikTok':
        base_options.update({
            'format': 'best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'cookiesfrombrowser': ('chrome',),
        })
    elif platform == 'Instagram':
        base_options.update({
            'format': 'best[ext=mp4]/best[height<=1080]/best',
            'merge_output_format': 'mp4',
            'cookiesfrombrowser': ('chrome',),
            'extract_flat': False,
            'ignoreerrors': True,
            'extractor_retries': 5,
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
            'no_warnings': True,
            'quiet': True,
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
            'no_warnings': True,
            'quiet': True,
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
    else:  # YouTube
        base_options.update({
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
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
    
    return base_options

# HTML 템플릿 (app.py와 동일)
HTML_FORM = '''
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>소셜 미디어 다운로더</title>
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
        width: 100%;
        max-width: 500px;
        text-align: center;
      }
      
      h1 {
        color: #333;
        margin-bottom: 30px;
        font-size: 2.5em;
        font-weight: 700;
      }
      
      .platform-info {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        display: none;
        align-items: center;
        gap: 10px;
        border-left: 4px solid #007bff;
      }
      
      .platform-info.show {
        display: flex;
      }
      
      .platform-icon {
        font-size: 1.5em;
      }
      
      .platform-name {
        font-weight: 600;
        color: #333;
      }
      
      .form-group {
        margin-bottom: 25px;
      }
      
      label {
        display: block;
        margin-bottom: 8px;
        color: #555;
        font-weight: 600;
        text-align: left;
      }
      
      input[type="url"] {
        width: 100%;
        padding: 15px;
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        font-size: 16px;
        transition: border-color 0.3s ease;
      }
      
      input[type="url"]:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
      
      button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        width: 100%;
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
      
      .loading {
        display: none;
        margin: 20px 0;
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
      
      .error {
        background: #ffe6e6;
        color: #d63031;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 4px solid #d63031;
      }
      
      .success {
        background: #e6ffe6;
        color: #00b894;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 4px solid #00b894;
      }
      
      .download-link {
        display: inline-block;
        background: #00b894;
        color: white;
        text-decoration: none;
        padding: 12px 25px;
        border-radius: 8px;
        font-weight: 600;
        margin-top: 10px;
        transition: background 0.3s ease;
      }
      
      .download-link:hover {
        background: #00a085;
      }
      
      .features {
        margin-top: 30px;
        text-align: left;
      }
      
      .features h3 {
        color: #333;
        margin-bottom: 15px;
      }
      
      .feature-list {
        list-style: none;
        padding: 0;
      }
      
      .feature-list li {
        padding: 8px 0;
        color: #666;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      
      .feature-list li i {
        color: #667eea;
        width: 20px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>🎬 소셜 미디어 다운로더</h1>
      
      <div class="platform-info" id="platformInfo">
        <i class="platform-icon" id="platformIcon"></i>
        <span class="platform-name" id="platformName"></span>
      </div>
      
      <form id="downloadForm" method="POST">
        <div class="form-group">
          <label for="url">동영상 URL:</label>
          <input type="url" id="url" name="url" placeholder="https://www.youtube.com/watch?v=..." required>
        </div>
        
        <button type="submit" id="downloadBtn">
          <i class="fas fa-download"></i> 다운로드
        </button>
      </form>
      
      <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>동영상을 다운로드하고 있습니다...</p>
      </div>
      
      {% if error %}
      <div class="error">
        <i class="fas fa-exclamation-triangle"></i> {{ error }}
      </div>
      {% endif %}
      
      {% if filename %}
      <div class="success">
        <i class="fas fa-check-circle"></i> 다운로드가 완료되었습니다!
        <br>
        <a href="/file/{{ filename }}" class="download-link">
          <i class="fas fa-download"></i> 파일 다운로드
        </a>
      </div>
      {% endif %}
      
      <div class="features">
        <h3>지원 플랫폼:</h3>
        <ul class="feature-list">
          <li><i class="fab fa-youtube"></i> YouTube</li>
          <li><i class="fab fa-tiktok"></i> TikTok</li>
          <li><i class="fab fa-instagram"></i> Instagram</li>
          <li><i class="fab fa-reddit"></i> Reddit</li>
          <li><i class="fab fa-twitter"></i> Twitter/X</li>
        </ul>
      </div>
    </div>
    
    <script>
      document.getElementById('url').addEventListener('input', function() {
        const url = this.value.trim();
        const urlLower = url.toLowerCase();
        
        if (url) {
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
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "파일이 존재하지 않습니다.", 404

if __name__ == '__main__':
    # 개발 모드 비활성화로 빠른 시작
    app.run(debug=False, host='0.0.0.0', port=3000, threaded=True) 