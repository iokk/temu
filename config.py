"""
TEMU 智能出图系统 V8.0
配置文件
核心作者: 企鹅

新增: Nano Banana Pro 模型支持, 4K 输出, 多种宽高比
"""
import os
from pathlib import Path
from typing import List, Optional
import random


class Config:
    """系统配置"""
    
    # ==================== 应用信息 ====================
    APP_NAME = "TEMU 智能出图系统"
    APP_VERSION = "V8.0"
    APP_AUTHOR = "企鹅"
    PAGE_TITLE = f"{APP_NAME} {APP_VERSION}"
    PAGE_ICON = "🎨"
    LAYOUT = "wide"
    
    # ==================== 认证配置 ====================
    ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "temu2024")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin888")
    
    # ==================== API 配置 ====================
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        return (
            os.getenv("GEMINI_API_KEY") or 
            os.getenv("GOOGLE_API_KEY") or 
            os.getenv("API_KEY")
        )
    
    # ==================== 模型配置 (Nano Banana) ====================
    # 默认使用 Nano Banana Pro
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-3-pro-image-preview")
    
    # 可用模型
    AVAILABLE_MODELS = {
        "🍌 Nano Banana Pro (推荐)": "gemini-3-pro-image-preview",
        "⚡ Nano Banana (快速)": "gemini-2.5-flash-image",
    }
    
    MODEL_DESCRIPTIONS = {
        "gemini-3-pro-image-preview": "专业级生成, 4K输出, 高质量文字渲染, 支持Thinking推理",
        "gemini-2.5-flash-image": "高速生成, 低延迟, 适合批量任务",
    }
    
    # 模型能力
    MODEL_CAPABILITIES = {
        "gemini-3-pro-image-preview": {
            "max_resolution": "4K",
            "resolutions": ["1K", "2K", "4K"],
            "max_input_images": 14,
            "thinking": True,
            "grounding": True,
        },
        "gemini-2.5-flash-image": {
            "max_resolution": "1K",
            "resolutions": ["1K"],
            "max_input_images": 3,
            "thinking": False,
            "grounding": False,
        },
    }
    
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "180"))
    
    # ==================== 图片宽高比 ====================
    ASPECT_RATIOS = {
        "1:1 正方形": "1:1",
        "4:3 横版": "4:3",
        "3:4 竖版": "3:4",
        "16:9 宽屏": "16:9",
        "9:16 手机屏": "9:16",
        "3:2 相机比例": "3:2",
        "2:3 肖像": "2:3",
        "21:9 超宽屏": "21:9",
    }
    
    # ==================== 图片分辨率 ====================
    RESOLUTIONS = {
        "1K 标准": "1K",
        "2K 高清": "2K",
        "4K 超高清": "4K",
    }
    
    # ==================== 图片风格预设 ====================
    STYLE_PRESETS = {
        "📷 产品摄影": "Professional product photography, studio lighting, clean background, high resolution, commercial quality",
        "🏠 生活场景": "Lifestyle photography, natural lighting, warm atmosphere, realistic home setting",
        "✨ 极简风格": "Minimalist style, clean composition, negative space, modern aesthetic",
        "🎨 艺术插画": "Artistic illustration style, vibrant colors, creative composition",
        "📸 电商主图": "E-commerce hero shot, white background, product centered, professional lighting",
        "🌟 高端奢华": "Luxury style, premium feel, elegant lighting, sophisticated composition",
        "🎯 信息图表": "Clean infographic style, clear typography, informative layout",
        "🔧 自定义": "",
    }
    
    # ==================== 配额配置 ====================
    DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "50"))
    DAILY_LIMIT_WITH_OWN_KEY = 9999
    
    # ==================== 禁用词预设 ====================
    EXCLUDE_PRESETS = {
        "🛡️ 标准": ["competitor logos", "brand names", "watermarks", "qr codes", "human faces", "children"],
        "🔒 严格": ["competitor logos", "brand names", "watermarks", "qr codes", "human faces", "children", "hands", "text overlays"],
        "🎨 宽松": ["competitor logos", "brand names", "watermarks"],
    }
    
    COMMON_EXCLUDE_OPTIONS = [
        "competitor logos", "brand names", "watermarks", "qr codes", 
        "human faces", "children", "hands", "models", "text overlays",
    ]
    
    # ==================== 数据目录 ====================
    BASE_DIR = Path(__file__).parent
    _data_dir: Optional[Path] = None
    _usage_file: Optional[Path] = None
    
    @classmethod
    def ensure_data_dir(cls):
        if cls._data_dir is not None:
            return
        for path_str in [os.getenv("DATA_DIR"), "/app/data", "/tmp/temu_data", str(cls.BASE_DIR / "data")]:
            if not path_str:
                continue
            try:
                path = Path(path_str)
                path.mkdir(parents=True, exist_ok=True)
                (path / ".test").write_text("test")
                (path / ".test").unlink()
                cls._data_dir = path
                cls._usage_file = path / "usage.json"
                return
            except Exception:
                continue
        cls._data_dir = cls.BASE_DIR / "data"
        cls._usage_file = cls._data_dir / "usage.json"
        cls._data_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== 提示语 ====================
    LOADING_TIPS = [
        "🍌 Nano Banana Pro 正在思考最佳构图...",
        "🎨 AI 正在为您的产品寻找完美角度...",
        "✨ 专业级图像即将生成...",
        "🚀 正在召唤 AI 创意大师...",
        "💫 创意正在酝酿中...",
        "🔮 AI 正在施展魔法...",
    ]
    
    SUCCESS_MESSAGES = [
        "🎉 太棒了！专业级图片已生成！",
        "✨ 完美！高质量产品图已就绪！",
        "🍌 Nano Banana Pro 交出满意答卷！",
        "🏆 恭喜！电商级图片已完成！",
    ]
    
    WELCOME_TIPS = [
        "Nano Banana Pro 支持 4K 超高清输出",
        "新增多种宽高比选择，适配各平台",
        "不满意？点击重新生成按钮再试一次",
        "Pro 模型支持复杂文字渲染",
    ]
    
    @classmethod
    def get_random_tip(cls, tip_type: str = "loading") -> str:
        tips = {"loading": cls.LOADING_TIPS, "success": cls.SUCCESS_MESSAGES, "welcome": cls.WELCOME_TIPS}
        return random.choice(tips.get(tip_type, cls.LOADING_TIPS))
    
    @classmethod
    def validate(cls) -> List[str]:
        errors = []
        if not cls.get_api_key():
            errors.append("未配置 GEMINI_API_KEY")
        return errors
