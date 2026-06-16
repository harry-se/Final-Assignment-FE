import json
import os

HISTORY_FILE = "chat_history.json"

def save_session_to_db(session_id, messages):
    """Lưu phiên chat hiện tại vào database hoặc file"""
    data = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: pass
            
    data[session_id] = messages
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_all_sessions_from_db():
    """Lấy toàn bộ danh sách phiên chat cũ"""
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}