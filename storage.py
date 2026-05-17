import json
import os
import threading
from datetime import datetime

STORAGE_FILE = "messages.json"
_lock = threading.Lock()

def save_message(username: str, text: str, message_id: int, reply_to_id: int = None):
    with _lock:
        messages = _load()
        messages.append({
            "username": username,
            "text": text,
            "timestamp": datetime.now().strftime("%H:%M"),
            "message_id": message_id,
            "reply_to_id": reply_to_id,
        })
        _write(messages)

def load_all() -> list:
    with _lock:
        return _load()

def clear():
    with _lock:
        _write([])
    print("🗑 messages.json очищен")

def count() -> int:
    return len(load_all())

def _load() -> list:
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ Ошибка чтения {STORAGE_FILE}: {e}")
        return []

def _write(messages: list):
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠ Ошибка записи {STORAGE_FILE}: {e}")
