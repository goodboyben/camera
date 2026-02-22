import http.server, socketserver, threading, subprocess, time, os, sys, ctypes
from ctypes import wintypes

PORT = 8000

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

subprocess.run(f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr ":{PORT}" ^| findstr "LISTENING"\') do taskkill /f /pid %a >nul 2>&1', shell=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=resource_path(""), **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

def get_default_browser_path():
    try:
        shlwapi = ctypes.windll.shlwapi
        pcchOut = wintypes.DWORD(0)
        
        # Ask Windows API for the required string buffer size
        shlwapi.AssocQueryStringW(0, 2, "http", "open", None, ctypes.byref(pcchOut))
        
        if pcchOut.value > 0:
            pszOut = ctypes.create_unicode_buffer(pcchOut.value)
            # Ask Windows API to fill the buffer with the executable path
            shlwapi.AssocQueryStringW(0, 2, "http", "open", pszOut, ctypes.byref(pcchOut))
            return pszOut.value
    except Exception:
        pass
    return None

def launch_browser():
    url = f"http://localhost:{PORT}/camera.html"
    exe_path = get_default_browser_path()
    
    if exe_path and os.path.exists(exe_path):
        exe_name = os.path.basename(exe_path).lower()
        chromium_browsers = ["chrome.exe", "msedge.exe", "brave.exe", "opera.exe", "vivaldi.exe"]
        
        if exe_name in chromium_browsers:
            subprocess.Popen([exe_path, f"--app={url}"])
        else:
            subprocess.Popen([exe_path, url])
    else:
        os.startfile(url)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    time.sleep(0.5)
    launch_browser()
    time.sleep(5)