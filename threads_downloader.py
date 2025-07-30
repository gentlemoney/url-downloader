#!/usr/bin/env python3
"""
Threads.net 동영상 다운로더
yt-dlp가 지원하지 않는 경우를 위한 대체 스크립트
"""

import re
import requests
import json
import sys
import os
from urllib.parse import urlparse, parse_qs

def extract_threads_video(url):
    """Threads URL에서 동영상을 추출합니다."""
    print(f"🔍 Threads URL 분석 중: {url}")
    
    # Threads URL 패턴 확인
    if 'threads.net' not in url:
        raise ValueError("올바른 Threads URL이 아닙니다.")
    
    # 모바일 User-Agent 사용
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # 페이지 다운로드
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html_content = response.text
        
        # 동영상 URL 패턴 찾기
        video_patterns = [
            r'"video_url":"([^"]+)"',
            r'"videoUrl":"([^"]+)"',
            r'"playable_url":"([^"]+)"',
            r'"src":"([^"]+\.mp4[^"]*)"',
            r'<video[^>]+src="([^"]+)"',
        ]
        
        video_url = None
        for pattern in video_patterns:
            match = re.search(pattern, html_content)
            if match:
                video_url = match.group(1)
                # 이스케이프 문자 처리
                video_url = video_url.replace('\\/', '/')
                video_url = video_url.replace('\\u0025', '%')
                break
        
        if not video_url:
            # JavaScript 렌더링된 콘텐츠에서 찾기
            json_pattern = r'<script[^>]*>window\._sharedData\s*=\s*({[^<]+})</script>'
            json_match = re.search(json_pattern, html_content)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    # 데이터 구조 탐색하여 비디오 URL 찾기
                    # (Threads의 데이터 구조는 복잡하고 자주 변경됨)
                    print("⚠️  JavaScript 데이터에서 동영상을 찾는 중...")
                except:
                    pass
        
        if video_url:
            print(f"✅ 동영상 URL 발견: {video_url[:50]}...")
            return video_url
        else:
            raise ValueError("동영상 URL을 찾을 수 없습니다. Threads가 구조를 변경했을 수 있습니다.")
            
    except requests.RequestException as e:
        raise Exception(f"네트워크 오류: {str(e)}")
    except Exception as e:
        raise Exception(f"오류 발생: {str(e)}")

def download_video(video_url, output_path):
    """동영상을 다운로드합니다."""
    print(f"📥 동영상 다운로드 중...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(video_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # 파일 크기 확인
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r진행률: {progress:.1f}%", end='', flush=True)
        
        print(f"\n✅ 다운로드 완료: {output_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ 다운로드 실패: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 threads_downloader.py [THREADS_URL]")
        print("예시: python3 threads_downloader.py https://www.threads.net/...")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        # 동영상 URL 추출
        video_url = extract_threads_video(url)
        
        # 파일명 생성
        output_filename = f"threads_video_{os.urandom(4).hex()}.mp4"
        output_path = os.path.join('downloads', output_filename)
        
        # 다운로드
        if download_video(video_url, output_path):
            print(f"\n🎉 성공! 파일 위치: {output_path}")
        else:
            print("\n😞 다운로드에 실패했습니다.")
            
    except Exception as e:
        print(f"\n❌ 오류: {str(e)}")
        print("\n💡 팁: Threads는 자주 구조를 변경합니다. 브라우저 개발자 도구를 사용해 직접 동영상을 찾아보세요.")
        sys.exit(1)

if __name__ == "__main__":
    main() 