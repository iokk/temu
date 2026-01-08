"""
TEMU 智能出图系统 - 配置文件
核心作者: 企鹅君
版本: V6.6 Zeabur Optimized
"""
import os
from pathlib import Path
from typing import List, Optional
import random


class Config:
    """系统配置类 - 所有配置项统一管理"""
    
    # ============ 应用基础配置 ============
    APP_NAME = "TEMU 智能出图系统"
    APP_VERSION = "V6.6"
    APP_AUTHOR = "企鹅"
    PAGE_TITLE = f"{APP_NAME} {APP_VERSION}"
    PAGE_ICON = "🎨"
    LAYOUT = "wide"
    
    # ============ 路径配置 ============
    BASE_DIR = Path(__file__).parent
    _data_dir: Optional[Path] = None
    _usage_file: Optional[Path] = None
    
    @classmethod
    @property
    def DATA_DIR(cls) -> Path:
        """获取数据目录（延迟初始化）"""
        if cls._data_dir is None:
            cls.ensure_data_dir()
        return cls._data_dir
    
    @classmethod
    @property
    def USAGE_FILE(cls) -> Path:
        """获取使用量文件路径"""
        if cls._usage_file is None:
            cls.ensure_data_dir()
        return cls._usage_file
    
    @classmethod
    def ensure_data_dir(cls):
        """确保数据目录存在"""
        if cls._data_dir is not None:
            return
            
        # 按优先级尝试不同目录
        candidates = [
            os.getenv("DATA_DIR"),
            "/tmp/temu_data",  # Zeabur 临时目录
            str(cls.BASE_DIR / "data"),
        ]
        
        for path_str in candidates:
            if path_str is None:
                continue
            try:
                path = Path(path_str)
                path.mkdir(parents=True, exist_ok=True)
                # 测试写入权限
                test_file = path / ".test"
                test_file.write_text("test")
                test_file.unlink()
                cls._data_dir = path
                cls._usage_file = path / "usage.json"
                return
            except Exception:
                continue
        
        # 最后备选：使用当前目录
        cls._data_dir = cls.BASE_DIR / "data"
        cls._usage_file = cls._data_dir / "usage.json"
        try:
            cls._data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
    
    # ============ 认证配置 ============
    ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "temu2024")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin888")
    ADMIN_PATH = os.getenv("ADMIN_PATH", "/admin")
    
    # ============ API 配置 ============
    # Gemini API Key - 支持多种环境变量名
    @classmethod
    @property
    def GEMINI_API_KEY(cls) -> Optional[str]:
        return (
            os.getenv("GEMINI_API_KEY") or 
            os.getenv("GOOGLE_API_KEY") or 
            os.getenv("API_KEY")
        )
    
    # 默认模型
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash-exp-image-generation")
    
    # 兼容旧配置
    IMAGE_MODEL = os.getenv("IMAGE_MODEL") or DEFAULT_MODEL
    
    # 可选模型列表
    AVAILABLE_MODELS = {
        "🧪 Gemini 2.0 Flash (推荐)": "gemini-2.0-flash-exp-image-generation",
        "🖼️ Imagen 3": "imagen-3.0-generate-002",
    }
    
    MODEL_DESCRIPTIONS = {
        "gemini-2.0-flash-exp-image-generation": "Gemini 2.0 实验版，多模态能力强，推荐使用",
        "imagen-3.0-generate-002": "Google Imagen 3，高质量图像生成",
    }
    
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "120"))
    
    # ============ 配额限制 ============
    DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "50"))
    DAILY_LIMIT_WITH_OWN_KEY = 9999
    
    # ============ 图片生成配置 ============
    DEFAULT_SIZE = (1024, 1024)
    
    SIZE_PRESETS = {
        "1:1 正方形（推荐）": (1024, 1024),
        "4:3 横版": (1024, 768),
        "3:4 竖版": (768, 1024),
        "16:9 宽屏": (1024, 576),
        "9:16 手机屏": (576, 1024),
        "自定义": None
    }
    
    DEFAULT_STYLE_STRENGTH = 0.3
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
    
    COMMON_EXCLUDE_OPTIONS = [
        "competitor logos", "brand names", "watermarks", "qr codes", 
        "website urls", "human faces", "children", "hands", "models",
        "text overlays", "price tags", "promotional text", "unrelated props",
        "cluttered background", "messy environment", "packaging", "labels"
    ]
    
    # ============ 日志和调试 ============
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # ============ 有趣的提示语 ============
    LOADING_TIPS = [
        "🎨 AI 正在为您的产品寻找最佳角度...",
        "✨ 让每一个像素都闪闪发光...",
        "🚀 正在召唤 AI 创意大师...",
        "🎭 AI 正在构思完美的场景...",
        "🌟 优质图片即将诞生...",
        "🔮 AI 正在施展魔法...",
        "🎪 精彩即将呈现...",
        "💫 创意正在酝酿中...",
        "🎯 精准定位产品亮点...",
        "🌈 为您的产品添加光芒...",
        "☕ AI 喝了口咖啡，马上回来...",
        "🎸 AI 正在为您的产品谱写视觉乐章...",
    ]
    
    SUCCESS_MESSAGES = [
        "🎉 太棒了！图片生成成功！",
        "✨ 完美！您的产品图片已就绪！",
        "🚀 搞定！高质量图片已生成！",
        "💯 漂亮！AI 交出了满意答卷！",
        "🌟 出色！这张图片一定能吸引眼球！",
        "🏆 恭喜！专业级电商图已就位！",
    ]
    
    ERROR_TIPS = [
        "😅 AI 打了个盹，请稍后重试",
        "🤔 遇到了一点小问题，换个姿势再来",
        "💪 别灰心，再试一次可能就成功了",
        "🔄 AI 正在热身，请稍候重试",
        "🛠️ 遇到技术问题，工程师已在路上",
    ]
    
    WELCOME_TIPS = [
        "高质量原图 + 合适的风格强度 = 完美电商图",
        "AI 会自动识别产品特征，让您的工作更轻松",
        "批量生成多种类型，一次搞定所有需求",
        "禁用词预设可以有效避免不合规内容",
        "场景图让产品更有生活气息，销量更好哦",
        "细节图能展示产品工艺，提升购买信心",
        "对比图是展示产品优势的利器",
        "规格图让买家一目了然，减少退货率",
    ]
    
    @classmethod
    def validate(cls) -> List[str]:
        """验证配置完整性"""
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
        """获取配置信息"""
        cls.ensure_data_dir()
        return {
            "应用名称": cls.APP_NAME,
            "版本": cls.APP_VERSION,
            "作者": cls.APP_AUTHOR,
            "数据目录": str(cls._data_dir),
            "每日免费额度": cls.DAILY_LIMIT,
            "默认模型": cls.DEFAULT_MODEL,
            "调试模式": cls.DEBUG
        }
    
    @classmethod
    def get_random_tip(cls, tip_type: str = "loading") -> str:
        """获取随机提示语"""
        tips_map = {
            "loading": cls.LOADING_TIPS,
            "success": cls.SUCCESS_MESSAGES,
            "error": cls.ERROR_TIPS,
            "welcome": cls.WELCOME_TIPS,
        }
        tips = tips_map.get(tip_type, cls.LOADING_TIPS)
        return random.choice(tips)
