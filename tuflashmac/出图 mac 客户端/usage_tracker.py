"""
TEMU 智能出图系统 V8.0
使用量追踪
核心作者: 企鹅
"""
import json
import hashlib
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple
import threading

from config import Config


class UsageTracker:
    _lock = threading.Lock()
    
    def __init__(self):
        Config.ensure_data_dir()
        self._ensure_file()
    
    @property
    def usage_file(self) -> Path:
        return Config._usage_file
    
    def _ensure_file(self):
        try:
            if self.usage_file and not self.usage_file.exists():
                self.usage_file.write_text("{}")
        except Exception:
            pass
    
    def _load(self) -> Dict:
        with self._lock:
            try:
                if self.usage_file and self.usage_file.exists():
                    content = self.usage_file.read_text()
                    return json.loads(content) if content.strip() else {}
            except Exception:
                pass
            return {}
    
    def _save(self, data: Dict):
        with self._lock:
            try:
                if self.usage_file:
                    self.usage_file.write_text(json.dumps(data, indent=2))
            except Exception:
                pass
    
    def get_user_id(self, session_state) -> str:
        if "user_id" not in session_state:
            unique = f"{id(session_state)}_{datetime.now().isoformat()}"
            session_state.user_id = hashlib.md5(unique.encode()).hexdigest()[:12]
        return session_state.user_id
    
    def get_usage(self, user_id: str) -> int:
        data = self._load()
        return data.get(date.today().isoformat(), {}).get(user_id, 0)
    
    def add_usage(self, user_id: str, count: int = 1):
        data = self._load()
        today = date.today().isoformat()
        if today not in data:
            data[today] = {}
            cutoff = (date.today() - timedelta(days=7)).isoformat()
            for k in list(data.keys()):
                if k < cutoff:
                    del data[k]
        data[today][user_id] = data[today].get(user_id, 0) + count
        self._save(data)
    
    def check_quota(self, user_id: str, using_own_key: bool) -> Tuple[bool, int]:
        if using_own_key:
            return True, Config.DAILY_LIMIT_WITH_OWN_KEY
        used = self.get_usage(user_id)
        remaining = Config.DAILY_LIMIT - used
        return remaining > 0, max(0, remaining)
    
    def get_stats(self) -> Dict:
        data = self._load()
        today_data = data.get(date.today().isoformat(), {})
        return {
            "total": sum(today_data.values()),
            "users": len(today_data),
            "details": sorted(today_data.items(), key=lambda x: -x[1]),
        }
    
    def clear_today(self):
        data = self._load()
        today = date.today().isoformat()
        if today in data:
            del data[today]
            self._save(data)
