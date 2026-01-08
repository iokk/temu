"""
TEMU 智能出图系统 - 使用量追踪
核心作者: 企鹅
"""
import json
import hashlib
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Tuple
import threading

from config import Config


class UsageTracker:
    """使用量追踪器"""
    
    _lock = threading.Lock()
    
    def __init__(self):
        Config.ensure_data_dir()
        self._ensure_file()
    
    @property
    def usage_file(self) -> Path:
        return Config._usage_file
    
    def _ensure_file(self):
        """确保数据文件存在"""
        try:
            if self.usage_file and not self.usage_file.exists():
                self.usage_file.write_text("{}")
        except Exception:
            pass
    
    def load_data(self) -> Dict:
        """加载数据"""
        with self._lock:
            try:
                if self.usage_file and self.usage_file.exists():
                    content = self.usage_file.read_text()
                    return json.loads(content) if content.strip() else {}
            except Exception:
                pass
            return {}
    
    def save_data(self, data: Dict):
        """保存数据"""
        with self._lock:
            try:
                if self.usage_file:
                    self.usage_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
            except Exception:
                pass
    
    def get_user_id(self, session_state) -> str:
        """获取用户标识"""
        if "user_id" not in session_state:
            unique = f"{id(session_state)}_{datetime.now().isoformat()}"
            session_state.user_id = hashlib.md5(unique.encode()).hexdigest()[:12]
        return session_state.user_id
    
    def get_today_usage(self, user_id: str) -> int:
        """获取今日使用量"""
        data = self.load_data()
        today = date.today().isoformat()
        return data.get(today, {}).get(user_id, 0)
    
    def increment_usage(self, user_id: str, count: int = 1):
        """增加使用量"""
        data = self.load_data()
        today = date.today().isoformat()
        
        if today not in data:
            data[today] = {}
            # 清理7天前数据
            self._cleanup(data)
        
        data[today][user_id] = data[today].get(user_id, 0) + count
        self.save_data(data)
    
    def _cleanup(self, data: Dict):
        """清理旧数据"""
        try:
            today = date.today()
            from datetime import timedelta
            cutoff = today - timedelta(days=7)
            keys_to_remove = [k for k in data.keys() if k < cutoff.isoformat()]
            for k in keys_to_remove:
                del data[k]
        except Exception:
            pass
    
    def check_quota(self, user_id: str, using_own_key: bool) -> Tuple[bool, int]:
        """检查配额"""
        if using_own_key:
            return True, Config.DAILY_LIMIT_WITH_OWN_KEY
        
        used = self.get_today_usage(user_id)
        remaining = Config.DAILY_LIMIT - used
        return remaining > 0, max(0, remaining)
    
    def get_today_stats(self) -> Dict:
        """获取今日统计"""
        data = self.load_data()
        today = date.today().isoformat()
        today_data = data.get(today, {})
        
        return {
            "total_usage": sum(today_data.values()),
            "active_users": len(today_data),
            "user_details": sorted(today_data.items(), key=lambda x: -x[1])
        }
    
    def clear_today_data(self):
        """清空今日数据"""
        data = self.load_data()
        today = date.today().isoformat()
        if today in data:
            del data[today]
            self.save_data(data)
