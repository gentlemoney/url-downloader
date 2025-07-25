from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

# 임시 저장 폴더
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML_FORM = '''
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <title>YouTube 다운로드</title>
  </head>
  <body>
    <h1>YouTube 영상 다운로드</h1>
    <form method="post" action="/download">
      <input type="text" name="url" placeholder="유튜브 링크를 입력하세요" size="50" required>
      <button type="submit">다운로드</button>
    </form>
    {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
    {% if filename %}
      <p>다운로드 완료! <a href="/file/{{ filename }}">여기서 받기</a></p>
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
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # 확장자 통일
            if not filename.endswith('.mp4'):
                filename = os.path.splitext(filename)[0] + '.mp4'
            base = os.path.basename(filename)
        return render_template_string(HTML_FORM, filename=base)
    except Exception as e:
        return render_template_string(HTML_FORM, error=f"다운로드 실패: {e}")

@app.route('/file/<filename>')
def file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "파일이 존재하지 않습니다.", 404

if __name__ == '__main__':
    app.run(debug=True) 