#!/usr/bin/env python3

import os
import time
import requests
import threading
import watchdog.events
from watchdog.observers.polling import PollingObserver
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment
JELLYFIN_URL = os.getenv("JELLYFIN_URL", "http://127.0.0.1:8096")
API_KEY = os.getenv("JELLYFIN_API_KEY", "")
MEDIA_FOLDER = os.getenv("MEDIA_FOLDER", "/data")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
LOG_TO_STDOUT = os.getenv("LOG_TO_STDOUT", "true").lower() == "true"
LOGFILE = os.getenv("LOGFILE", "/var/log/watchertoucher.log")
DELAY_SECONDS = int(os.getenv("DELAY_SECONDS", 60))
PO_TIMEOUT = int(os.getenv("POLL_TIMEOUT", 5))
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
VERSION = "0.2.0"

FILETYPES = [
    "*.mkv", "*.mp4", "*.avi", "*.m4v", "*.mov", "*.ts", "*.vob", "*.webm",
    "*.mp3", "*.mp2", "*.ogg", "*.flac", "*.m4a", "*.srt", "*.sub",
    "*.ass", "*.idx", "*.smi"
]
IGNORED_FILES = ["this.file", "that.file"]

# State control
request_scheduled = False
scheduled_refresh_time = 0
lock = threading.Lock()

def log_message(message, end="\n"):
    timestamp = datetime.now().strftime(DATE_FORMAT)
    formatted = f"{timestamp} {message}"
    
    if LOG_TO_STDOUT:
        print(formatted, end=end)
    if LOG_TO_FILE:
        try:
            with open(LOGFILE, "a") as f:
                f.write(formatted + end)
        except Exception as e:
            print(f"[ERROR] Cannot write to log file: {e}")

def is_scan_running():
    try:
        headers = {"Authorization": f'MediaBrowser Token="{API_KEY}", Client="watchertoucher {VERSION}"'}
        response = requests.get(f"{JELLYFIN_URL}/ScheduledTasks", headers=headers, timeout=10)
        if response.status_code == 200:
            for task in response.json():
                if task.get("Name") == "Scan Media Library" and task.get("State") == "Running":
                    log_message("Library refresh already in progress, re-scheduling at ", end="")
                    return True
    except Exception as e:
        log_message(f"[ERROR] Jellyfin API connection failed: {e}")
    return False

def send_refresh_request():
    global request_scheduled, scheduled_refresh_time
    time.sleep(DELAY_SECONDS)

    if is_scan_running():
        next_time = time.time() + DELAY_SECONDS
        with lock:
            scheduled_refresh_time = next_time
        log_message(f"{datetime.fromtimestamp(next_time).strftime(DATE_FORMAT)}")
        threading.Thread(target=send_refresh_request, daemon=True).start()
        return

    try:
        headers = {"Authorization": f'MediaBrowser Token="{API_KEY}", Client="watchertoucher {VERSION}"'}
        response = requests.post(f"{JELLYFIN_URL}/Library/Refresh", headers=headers, timeout=10)
        with lock:
            request_scheduled = False
            scheduled_refresh_time = 0

        if response.status_code == 204:
            log_message("Library refresh triggered successfully.")
        else:
            log_message(f"[ERROR] Failed to refresh: {response.status_code} {response.text}")
    except Exception as e:
        log_message(f"[ERROR] Jellyfin API connection failed: {e}")

def queue_refresh():
    global request_scheduled, scheduled_refresh_time
    with lock:
        now = time.time()
        if request_scheduled and scheduled_refresh_time > now:
            log_message(f", library refresh in {int(scheduled_refresh_time - now)} seconds")
            return
        scheduled_refresh_time = now + DELAY_SECONDS
        request_scheduled = True
    threading.Thread(target=send_refresh_request, daemon=True).start()
    log_message(f", refresh scheduled at {datetime.fromtimestamp(scheduled_refresh_time).strftime(DATE_FORMAT)}")

class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(patterns=FILETYPES, ignore_patterns=IGNORED_FILES,
                         ignore_directories=False, case_sensitive=False)

    def on_created(self, event):
        log_message(f"File created: {event.src_path}", end="")
        queue_refresh()

    def on_deleted(self, event):
        log_message(f"File removed: {event.src_path}", end="")
        queue_refresh()

    def on_moved(self, event):
        log_message(f"File moved: {event.src_path} → {event.dest_path}", end="")
        queue_refresh()

def main():
    log_message(f"watchertoucher {VERSION} started. Watching {MEDIA_FOLDER}")
    observer = PollingObserver(timeout=PO_TIMEOUT)
    observer.schedule(Handler(), path=MEDIA_FOLDER, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_message("Shutting down...")
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()
