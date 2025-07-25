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
    <title>YouTube 다운로드</title>
    <style>
      body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
      h1 { color: #333; text-align: center; }
      input[type="text"] { width: 70%; padding: 10px; margin-right: 10px; }
      button { padding: 10px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; }
      button:hover { background-color: #0056b3; }
      .error { color: red; margin-top: 10px; }
      .success { color: green; margin-top: 10px; }
    </style>
  </head>
  <body>
    <h1>YouTube 영상 다운로드</h1>
    <form method="post" action="/download">
      <input type="text" name="url" placeholder="유튜브 링크를 입력하세요" size="50" required>
      <button type="submit">다운로드</button>
    </form>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
    {% if filename %}
      <p class="success">다운로드 완료! <a href="/file/{{ filename }}">여기서 받기</a></p>
    {% endif %}
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