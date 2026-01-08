"""
TEMU 智能出图系统 - 使用量追踪
核心作者: 企鹅

追踪用户每日使用量，实施配额限制
"""
import json
import hashlib
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Tuple

from config import Config


class UsageTracker:
    """使用量追踪器"""
    
    def __init__(self):
        # 先确保数据目录存在
        Config.ensure_data_dir()
        self.usage_file = Config.USAGE_FILE
        self._ensure_file()
    
    def _ensure_file(self):
        """确保数据文件存在"""
        try:
            if not self.usage_file.exists():
                self.usage_file.write_text(json.dumps({}, indent=2))
        except Exception as e:
            print(f"创建使用数据文件失败: {e}")
    
    def load_data(self) -> Dict:
        """加载使用量数据"""
        try:
            return json.loads(self.usage_file.read_text())
        except Exception:
            return {}
    
    def save_data(self, data: Dict):
        """保存使用量数据"""
        try:
            self.usage_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"保存使用数据失败: {e}")
    
    def get_user_id(self, session_state) -> str:
        """
        获取用户标识（基于 session）
        
        Args:
            session_state: Streamlit session state
            
        Returns:
            用户唯一ID
        """
        if "user_id" not in session_state:
            # 用 session ID + 时间戳生成唯一标识
            session_state.user_id = hashlib.md5(
                f"{id(session_state)}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
        return session_state.user_id
    
    def get_today_usage(self, user_id: str) -> int:
        """
        获取用户今日使用量
        
        Args:
            user_id: 用户ID
            
        Returns:
            今日已使用数量
        """
        data = self.load_data()
        today = date.today().isoformat()
        
        if today not in data:
            data[today] = {}
        
        return data.get(today, {}).get(user_id, 0)
    
    def increment_usage(self, user_id: str, count: int = 1):
        """
        增加使用量
        
        Args:
            user_id: 用户ID
            count: 增加的数量
        """
        data = self.load_data()
        today = date.today().isoformat()
        
        if today not in data:
            data[today] = {}
        
        data[today][user_id] = data[today].get(user_id, 0) + count
        self.save_data(data)
    
    def check_quota(self, user_id: str, using_own_key: bool) -> Tuple[bool, int]:
        """
        检查配额
        
        Args:
            user_id: 用户ID
            using_own_key: 是否使用自己的 API Key
            
        Returns:
            (是否可用, 剩余数量)
        """
        if using_own_key:
            return True, Config.DAILY_LIMIT_WITH_OWN_KEY
        
        used = self.get_today_usage(user_id)
        remaining = Config.DAILY_LIMIT - used
        return remaining > 0, max(0, remaining)
    
    def get_today_stats(self) -> Dict:
        """
        获取今日统计数据
        
        Returns:
            统计信息字典
        """
        data = self.load_data()
        today = date.today().isoformat()
        today_data = data.get(today, {})
        
        total_usage = sum(today_data.values())
        active_users = len(today_data)
        
        return {
            "total_usage": total_usage,
            "active_users": active_users,
            "user_details": sorted(today_data.items(), key=lambda x: -x[1])
        }
    
    def clear_today_data(self):
        """清空今日数据"""
        data = self.load_data()
        today = date.today().isoformat()
        if today in data:
            del data[today]
            self.save_data(data)
