"""
TEMU 智能出图系统 - 配置文件
核心作者: 企鹅
版本: V6.5 Refactored
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """系统配置类 - 所有配置项统一管理"""
    
    # ============ 应用基础配置 ============
    APP_NAME = "TEMU 智能出图系统"
    APP_VERSION = "V6.5"
    APP_AUTHOR = "企鹅"
    PAGE_TITLE = f"{APP_NAME} {APP_VERSION}"
    PAGE_ICON = "🎨"
    LAYOUT = "wide"
    
    # ============ 路径配置 ============
    BASE_DIR = Path(__file__).parent
    DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))  # Docker 持久化目录
    USAGE_FILE = DATA_DIR / "usage.json"
    
    @classmethod
    def ensure_data_dir(cls):
        """确保数据目录存在（延迟初始化）"""
        try:
            cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # 如果无法创建 /data，使用当前目录
            cls.DATA_DIR = cls.BASE_DIR / "data"
            cls.USAGE_FILE = cls.DATA_DIR / "usage.json"
            cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # ============ 认证配置 ============
    # 访问密码（团队共享密码）
    ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "temu2024")
    
    # 管理员密码（可查看统计数据）
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin888")
    
    # 管理员访问路径（用于隐藏管理功能入口）
    ADMIN_PATH = os.getenv("ADMIN_PATH", "/admin")
    
    # ============ API 配置 ============
    # Gemini API Key（团队共享）
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    # Gemini 模型配置
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-2.0-flash-exp")
    
    # API 请求超时（秒）
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "120"))
    
    # ============ 配额限制 ============
    # 每人每天免费额度（使用团队 API Key）
    DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "50"))
    
    # 使用个人 API Key 的额度（基本不限）
    DAILY_LIMIT_WITH_OWN_KEY = 9999
    
    # ============ 图片生成配置 ============
    # 默认图片尺寸
    DEFAULT_SIZE = (1024, 1024)
    
    # 支持的尺寸预设
    SIZE_PRESETS = {
        "1:1 正方形（推荐）": (1024, 1024),
        "4:3 横版": (1024, 768),
        "3:4 竖版": (768, 1024),
        "16:9 宽屏": (1024, 576),
        "9:16 手机屏": (576, 1024),
        "自定义": None
    }
    
    # 默认风格强度
    DEFAULT_STYLE_STRENGTH = 0.3
    
    # 风格强度范围
    STYLE_STRENGTH_MIN = 0.0
    STYLE_STRENGTH_MAX = 1.0
    STYLE_STRENGTH_STEP = 0.05
    
    # ============ 禁用词预设 ============
    EXCLUDE_PRESETS = {
        "🛡️ 标准（推荐）": [
            "competitor logos", "brand names", "watermarks", 
            "qr codes", "website urls", "human faces", "children"
        ],
        "🔒 严格": [
            "competitor logos", "brand names", "watermarks", 
            "qr codes", "website urls", "human faces", "children", 
            "hands", "models", "text overlays", "price tags"
        ],
        "🎨 宽松": [
            "competitor logos", "brand names", "watermarks", "qr codes"
        ],
        "✨ 自定义": []
    }
    
    # 可选禁用词
    COMMON_EXCLUDE_OPTIONS = [
        "competitor logos", "brand names", "watermarks", "qr codes", 
        "website urls", "human faces", "children", "hands", "models",
        "text overlays", "price tags", "promotional text", "unrelated props",
        "cluttered background", "messy environment", "packaging", "labels"
    ]
    
    # ============ 日志配置 ============
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # ============ 开发调试配置 ============
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> list[str]:
        """验证配置完整性，返回错误列表"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("未配置 GEMINI_API_KEY 环境变量")
        
        if not cls.ACCESS_PASSWORD:
            errors.append("未配置 ACCESS_PASSWORD")
            
        if not cls.ADMIN_PASSWORD:
            errors.append("未配置 ADMIN_PASSWORD")
        
        return errors
    
    @classmethod
    def get_info(cls) -> dict:
        """获取配置信息（用于显示）"""
        return {
            "应用名称": cls.APP_NAME,
            "版本": cls.APP_VERSION,
            "作者": cls.APP_AUTHOR,
            "数据目录": str(cls.DATA_DIR),
            "每日免费额度": cls.DAILY_LIMIT,
            "模型": cls.IMAGE_MODEL,
            "调试模式": cls.DEBUG
        }
