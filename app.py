from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import uuid
import logging

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 임시 저장 폴더
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML_FORM = '''
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube 다운로드 - gptkimisa.com</title>
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
        max-width: 600px;
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
        margin-bottom: 30px;
        font-size: 2em;
        font-weight: 300;
      }
      
      .subtitle {
        color: #666;
        margin-bottom: 30px;
        font-size: 1.1em;
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
        <i class="fab fa-youtube"></i>
      </div>
      <h1>YouTube 영상 다운로드</h1>
      <p class="subtitle">간편하고 빠른 유튜브 영상 다운로드 서비스</p>
      
      <form method="post" action="/download" id="downloadForm">
        <div class="form-group">
          <div class="input-group">
            <input type="text" name="url" placeholder="유튜브 링크를 입력하세요" required>
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
      document.getElementById('downloadForm').addEventListener('submit', function() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('downloadBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> 처리중...';
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
    
    # 고유 파일명 생성
    outtmpl = os.path.join(DOWNLOAD_FOLDER, f"{uuid.uuid4()}.%(ext)s")
    
    ydl_opts = {
        'outtmpl': outtmpl,
        'format': 'best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'ignoreerrors': False,
        'nocheckcertificate': True,
        'extractor_retries': 3,
    }
    
    try:
        logger.info(f"다운로드 시작: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 먼저 정보만 추출해서 영상이 접근 가능한지 확인
            info = ydl.extract_info(url, download=False)
            logger.info(f"영상 제목: {info.get('title', 'Unknown')}")
            
            # 실제 다운로드 실행
            ydl.download([url])
            
            # 다운로드된 파일 찾기
            filename = ydl.prepare_filename(info)
            if not filename.endswith('.mp4'):
                filename = os.path.splitext(filename)[0] + '.mp4'
            
            base = os.path.basename(filename)
            logger.info(f"다운로드 완료: {base}")
            
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
    app.run(debug=True) 