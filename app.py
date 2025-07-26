from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os
import uuid
import logging
import requests
import json
import re
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 다운로드 폴더 설정
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def normalize_threads_url(url):
    """Threads URL을 정규화합니다."""
    # Threads URL 패턴 매칭
    threads_patterns = [
        r'(https?://(?:www\.)?threads\.net/@[^\s]+)',
        r'(https?://(?:www\.)?threads\.net/t/[^\s]+)',
        r'(https?://(?:www\.)?threads\.net/thread/[^\s]+)',
    ]
    
    for pattern in threads_patterns:
        match = re.search(pattern, url)
        if match:
            extracted_url = match.group(1)
            logger.info(f"Threads URL 추출: {url} -> {extracted_url}")
            return extracted_url
    
    return url

def normalize_facebook_url(url):
    """Facebook URL을 정규화합니다."""
    # Facebook URL 패턴 매칭
    facebook_patterns = [
        r'(https?://(?:www\.)?facebook\.com/[^\s]+)',
        r'(https?://(?:www\.)?fb\.com/[^\s]+)',
        r'(https?://(?:www\.)?facebook\.com/watch/[^\s]+)',
    ]
    
    for pattern in facebook_patterns:
        match = re.search(pattern, url)
        if match:
            extracted_url = match.group(1)
            logger.info(f"Facebook URL 추출: {url} -> {extracted_url}")
            return extracted_url
    
    return url

def normalize_twitter_url(url):
    """Twitter/X URL을 정규화합니다."""
    # Twitter/X URL 패턴 매칭
    twitter_patterns = [
        r'(https?://(?:www\.)?twitter\.com/[^\s]+)',
        r'(https?://(?:www\.)?x\.com/[^\s]+)',
        r'(https?://(?:www\.)?twitter\.com/i/status/[^\s]+)',
        r'(https?://(?:www\.)?x\.com/i/status/[^\s]+)',
    ]
    
    for pattern in twitter_patterns:
        match = re.search(pattern, url)
        if match:
            extracted_url = match.group(1)
            logger.info(f"Twitter/X URL 추출: {url} -> {extracted_url}")
            return extracted_url
    
    return url

def normalize_reddit_url(url):
    """Reddit URL을 정규화합니다."""
    # Reddit URL 패턴 매칭
    reddit_patterns = [
        r'(https?://(?:www\.)?reddit\.com/r/[^\s]+)',
        r'(https?://(?:www\.)?reddit\.com/comments/[^\s]+)',
        r'(https?://(?:www\.)?redd\.it/[^\s]+)',
    ]
    
    for pattern in reddit_patterns:
        match = re.search(pattern, url)
        if match:
            extracted_url = match.group(1)
            logger.info(f"Reddit URL 추출: {url} -> {extracted_url}")
            return extracted_url
    
    return url

def detect_platform(url):
    """URL에서 플랫폼을 감지합니다."""
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube', 'fab fa-youtube', '#FF0000'
    elif 'tiktok.com' in url_lower:
        return 'TikTok', 'fab fa-tiktok', '#000000'
    elif 'instagram.com' in url_lower:
        return 'Instagram', 'fab fa-instagram', '#E4405F'
    elif 'reddit.com' in url_lower:
        return 'Reddit', 'fab fa-reddit', '#FF4500'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'Twitter/X', 'fab fa-twitter', '#1DA1F2'
    else:
        return 'Unknown', 'fas fa-question', '#6c757d'

def get_platform_specific_options(platform):
    """플랫폼별 최적화된 yt-dlp 옵션을 반환합니다."""
    base_options = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'ignoreerrors': True,
        'nocheckcertificate': True,
        'extractor_retries': 3,
        'format': 'best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'cookiesfrombrowser': ('chrome',),
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractaudio': False,
        'audioformat': 'mp3',
        'audioquality': '0',
        'recodevideo': 'mp4',
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
        'prefer_ffmpeg': True,
        'keepvideo': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'subtitleslangs': ['ko', 'en'],
        'skip_download': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'file_access_retries': 3
    }
    
    if platform == 'TikTok':
        base_options.update({
            'format': 'best[ext=mp4]/best',
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
            'subtitleslangs': ['ko', 'en'],
            'skip_download': False,
            'outtmpl': '%(title)s.%(ext)s',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.tiktok.com/',
                'Origin': 'https://www.tiktok.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'DNT': '1',
            },
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'file_access_retries': 5
        })
    elif platform == 'Instagram':
        base_options.update({
            'format': 'best[ext=mp4]/best',
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
            'subtitleslangs': ['ko', 'en'],
            'skip_download': False,
            'outtmpl': '%(title)s.%(ext)s',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.instagram.com/',
                'Origin': 'https://www.instagram.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'DNT': '1',
            },
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'file_access_retries': 5
        })
    elif platform == 'Reddit':
        base_options.update({
            'format': 'best[ext=mp4]/best',
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
            'subtitleslangs': ['ko', 'en'],
            'skip_download': False,
            'outtmpl': '%(title)s.%(ext)s',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.reddit.com/',
                'Origin': 'https://www.reddit.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'DNT': '1',
            },
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'file_access_retries': 5
        })
    elif platform == 'Twitter/X':
        base_options.update({
            'format': 'best[ext=mp4]/best',
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
            'subtitleslangs': ['ko', 'en'],
            'skip_download': False,
            'outtmpl': '%(title)s.%(ext)s',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://twitter.com/',
                'Origin': 'https://twitter.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'DNT': '1',
            },
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'file_access_retries': 5
        })
    else:  # YouTube 및 기타
        base_options.update({
            'format': 'best[ext=mp4]/best',
            'merge_output_format': 'mp4',
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
        margin-bottom: 30px;
      }
      
      .logo h1 {
        color: #333;
        font-size: 2.5em;
        margin-bottom: 10px;
      }
      
      .logo p {
        color: #666;
        font-size: 1.1em;
      }
      
      .input-group {
        margin-bottom: 30px;
      }
      
      .url-input {
        width: 100%;
        padding: 15px 20px;
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        font-size: 16px;
        transition: all 0.3s ease;
        margin-bottom: 15px;
      }
      
      .url-input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
      
      .download-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 40px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
      }
      
      .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
      }
      
      .download-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
      }
      
      .platform-info {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
        font-size: 14px;
      }
      
      .platform-icon {
        font-size: 24px;
        margin-right: 10px;
      }
      
      .platform-name {
        font-weight: bold;
        color: #333;
      }
      
      .result {
        margin-top: 30px;
        padding: 20px;
        border-radius: 10px;
        font-weight: bold;
      }
      
      .success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
      }
      
      .error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
      }
      
      .download-link {
        display: inline-block;
        background: #28a745;
        color: white;
        text-decoration: none;
        padding: 10px 20px;
        border-radius: 5px;
        margin-top: 10px;
        transition: background 0.3s ease;
      }
      
      .download-link:hover {
        background: #218838;
      }
      
      .platforms {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin: 30px 0;
      }
      
      .platform-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
        transition: all 0.3s ease;
      }
      
      .platform-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
      }
      
      .platform-item i {
        font-size: 2em;
        margin-bottom: 8px;
      }
      
      .platform-item span {
        font-weight: bold;
        color: #333;
      }
      
      .platform-item small {
        color: #666;
        font-size: 0.8em;
        margin-top: 5px;
      }
      
      .features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 40px;
      }
      
      .feature {
        text-align: center;
        padding: 20px;
      }
      
      .feature i {
        font-size: 2.5em;
        color: #667eea;
        margin-bottom: 15px;
      }
      
      .feature h3 {
        color: #333;
        margin-bottom: 10px;
      }
      
      .feature p {
        color: #666;
        line-height: 1.5;
      }
      
      .loading {
        display: none;
        margin: 20px 0;
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
      
      @media (max-width: 768px) {
        .container {
          padding: 20px;
        }
        
        .logo h1 {
          font-size: 2em;
        }
        
        .platforms {
          grid-template-columns: repeat(2, 1fr);
        }
        
        .features {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="logo">
        <h1><i class="fas fa-download"></i> 소셜 미디어 다운로드</h1>
        <p>YouTube, TikTok, Instagram, Reddit, Twitter/X 비디오를 쉽게 다운로드하세요</p>
      </div>
      
      <form method="POST" action="/download" id="downloadForm">
        <div class="input-group">
          <input type="text" name="url" id="urlInput" class="url-input" placeholder="비디오 URL을 입력하세요..." required>
          <button type="submit" class="download-btn" id="downloadBtn">
            <i class="fas fa-download"></i> 다운로드
          </button>
        </div>
        
        <div class="platform-info" id="platformInfo" style="display: none;">
          <i class="platform-icon" id="platformIcon"></i>
          <span class="platform-name" id="platformName"></span>
        </div>
        
        <div class="loading" id="loading">
          <div class="spinner"></div>
          <p>다운로드 중...</p>
        </div>
      </form>
      
      <div class="platforms">
        <div class="platform-item">
          <i class="fab fa-youtube" style="color: #FF0000;"></i>
          <span>YouTube</span>
          <small style="color: #666; font-size: 0.8em;">(Videos, Shorts)</small>
        </div>
        <div class="platform-item">
          <i class="fab fa-tiktok" style="color: #000000;"></i>
          <span>TikTok</span>
          <small style="color: #666; font-size: 0.8em;">(Videos)</small>
        </div>
        <div class="platform-item">
          <i class="fab fa-instagram" style="color: #E4405F;"></i>
          <span>Instagram</span>
          <small style="color: #666; font-size: 0.8em;">(Reels, Stories)</small>
        </div>
        <div class="platform-item">
          <i class="fab fa-reddit" style="color: #FF4500;"></i>
          <span>Reddit</span>
          <small style="color: #666; font-size: 0.8em;">(Videos, GIFs)</small>
        </div>
        <div class="platform-item">
          <i class="fab fa-twitter" style="color: #1DA1F2;"></i>
          <span>Twitter/X</span>
        </div>
      </div>
      
      <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 5px; font-size: 0.9em; color: #856404;">
        <i class="fas fa-info-circle"></i>
        <strong>Instagram 팁:</strong> Reels, Stories, Posts 비디오를 지원합니다. 일부 콘텐츠는 로그인이 필요할 수 있습니다.
      </div>
      <div style="margin-top: 10px; padding: 10px; background: #d1ecf1; border-radius: 5px; font-size: 0.9em; color: #0c5460;">
        <i class="fas fa-info-circle"></i>
        <strong>Reddit 팁:</strong> Reddit Videos, GIFs, v.redd.it 링크를 지원합니다. 대부분 공개 콘텐츠입니다.
        <br><small style="color: #0a4b52;">💡 Reddit은 공유 버튼이 없어서 브라우저 주소창의 URL을 복사해서 사용하세요!</small>
        <br><small style="color: #0a4b52;">📝 예시: https://www.reddit.com/r/aivideo/comments/1m9hn4u/cool_veo_3_ability/</small>
      </div>
      <div style="margin-top: 10px; padding: 10px; background: #e8f5e8; border-radius: 5px; font-size: 0.9em; color: #155724;">
        <i class="fas fa-info-circle"></i>
        <strong>Twitter/X 팁:</strong> Twitter와 X.com 비디오를 지원합니다. 공개 트윗의 비디오만 다운로드 가능합니다.
        <br><small style="color: #0f5132;">💡 Twitter/X는 공유 버튼을 통해 링크를 복사하거나 브라우저 주소창의 URL을 사용하세요!</small>
        <br><small style="color: #0f5132;">📝 예시: https://twitter.com/username/status/1234567890</small>
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
          // URL을 서버로 보내서 플랫폼 감지 (간단한 클라이언트 사이드 감지)
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
          }
          
          document.getElementById('platformName').textContent = platform;
          document.getElementById('platformIcon').className = icon;
          document.getElementById('platformIcon').style.color = color;
          document.getElementById('platformInfo').style.display = 'flex';
        } else {
          document.getElementById('platformInfo').style.display = 'none';
        }
      });
      
      document.getElementById('downloadForm').addEventListener('submit', function() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('downloadBtn').textContent = '다운로드 중...';
      });
      
      // 페이지 로드 시 URL이 있으면 플랫폼 감지
      const urlInput = document.getElementById('urlInput');
      if (urlInput.value) {
        urlInput.dispatchEvent(new Event('input'));
      }
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
    
    # Facebook URL 정규화
    if platform == 'Facebook':
        original_url = url
        url = normalize_facebook_url(url)
        logger.info(f"Facebook URL 정규화: {original_url} -> {url}")
    
    # Threads URL 정규화
    if platform == 'Threads':
        original_url = url
        url = normalize_threads_url(url)
        logger.info(f"Threads URL 정규화: {original_url} -> {url}")
    
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
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "파일이 존재하지 않습니다.", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(debug=False, host=host, port=port) 