import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import webbrowser
import time
import os
import sys

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader - 서버 관리")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # 서버 프로세스
        self.server_process = None
        self.server_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="🎬 YouTube Downloader", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 서버 상태
        self.status_label = ttk.Label(main_frame, text="서버 상태: 중지됨", 
                                     font=("Arial", 12))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="서버 시작", 
                                      command=self.start_server, width=15)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="서버 중지", 
                                     command=self.stop_server, width=15, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # 브라우저 열기 버튼
        self.browser_button = ttk.Button(main_frame, text="브라우저에서 열기", 
                                        command=self.open_browser, width=20, state="disabled")
        self.browser_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="서버 로그", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, width=45, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_server(self):
        if self.server_running:
            return
            
        self.log_message("서버 시작 중...")
        
        def run_server():
            try:
                # 현재 디렉토리에서 app.py 실행
                self.server_process = subprocess.Popen(
                    [sys.executable, "app.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                self.server_running = True
                self.root.after(0, self.update_ui_started)
                self.log_message("서버가 시작되었습니다!")
                
                # 서버 출력 읽기
                for line in iter(self.server_process.stdout.readline, ''):
                    if line:
                        self.root.after(0, lambda l=line: self.log_message(l.strip()))
                        
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"오류: {str(e)}"))
                self.root.after(0, self.update_ui_stopped)
        
        threading.Thread(target=run_server, daemon=True).start()
        
    def stop_server(self):
        if not self.server_running or not self.server_process:
            return
            
        self.log_message("서버 중지 중...")
        
        try:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            self.log_message("서버가 중지되었습니다.")
        except subprocess.TimeoutExpired:
            self.server_process.kill()
            self.log_message("서버를 강제 종료했습니다.")
        except Exception as e:
            self.log_message(f"서버 중지 오류: {str(e)}")
        
        self.server_running = False
        self.update_ui_stopped()
        
    def update_ui_started(self):
        self.status_label.config(text="서버 상태: 실행 중", foreground="green")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.browser_button.config(state="normal")
        
    def update_ui_stopped(self):
        self.status_label.config(text="서버 상태: 중지됨", foreground="red")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.browser_button.config(state="disabled")
        
    def open_browser(self):
        try:
            webbrowser.open("http://localhost:3000")
            self.log_message("브라우저를 열었습니다.")
        except Exception as e:
            self.log_message(f"브라우저 열기 오류: {str(e)}")
            
    def on_closing(self):
        if self.server_running:
            self.stop_server()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 