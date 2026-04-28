"""
TEMU 智能出图系统 V8.0
Gemini AI 客户端 - 支持 Nano Banana Pro
核心作者: 企鹅

支持功能:
- Nano Banana Pro (gemini-3-pro-image-preview): 4K, Thinking, 14张参考图
- Nano Banana (gemini-2.5-flash-image): 快速生成
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, List
from PIL import Image
import io
import json
import time

from google import genai
from google.genai import types


@dataclass
class ImageResult:
    """图片生成结果"""
    image: Image.Image
    raw_response: Any
    thinking_images: List[Image.Image] = None  # Thinking 过程中的草图


@dataclass
class ProductAnalysis:
    """产品分析结果"""
    product_description: str
    key_features: List[str]
    material_guess: str
    color_scheme: str
    suggested_scene: str


class GeminiClient:
    """Gemini AI 客户端 - Nano Banana 系列"""

    def __init__(self, api_key: str, model: str = "gemini-3-pro-image-preview", max_retries: int = 3):
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.client = genai.Client(api_key=api_key)
        
        # 模型能力
        self.is_pro = "pro" in model.lower()
        self.supports_4k = self.is_pro
        self.supports_thinking = self.is_pro

    def _retry(self, func, *args, **kwargs):
        """带重试的调用"""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                err = str(e).lower()
                if any(x in err for x in ["timeout", "rate", "503", "429", "retry"]):
                    time.sleep((2 ** attempt) + 1)
                    continue
                break
        raise last_error

    def analyze_image(self, image: Image.Image) -> ProductAnalysis:
        """分析产品图片"""
        buf = io.BytesIO()
        img = image.copy()
        if img.width > 1024 or img.height > 1024:
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        img.save(buf, format="PNG", optimize=True)
        img_data = buf.getvalue()
        
        prompt = """Analyze this product image and return JSON only:
{
    "product_description": "Brief description",
    "key_features": ["Feature 1", "Feature 2", "Feature 3"],
    "material_guess": "Material",
    "color_scheme": "Colors",
    "suggested_scene": "Usage scenario"
}
Return ONLY valid JSON."""
        
        def call_api():
            cfg = types.GenerateContentConfig(response_modalities=["TEXT"])
            return self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[types.Part.from_bytes(data=img_data, mime_type="image/png"), prompt],
                config=cfg,
            )
        
        try:
            resp = self._retry(call_api)
            text = resp.text.strip() if resp.text else ""
            for mark in ["```json", "```"]:
                text = text.replace(mark, "")
            data = json.loads(text.strip())
            return ProductAnalysis(
                product_description=data.get("product_description", "Product"),
                key_features=data.get("key_features", ["High Quality"])[:5],
                material_guess=data.get("material_guess", ""),
                color_scheme=data.get("color_scheme", ""),
                suggested_scene=data.get("suggested_scene", "home setting"),
            )
        except Exception:
            return ProductAnalysis(
                product_description="Product",
                key_features=["High Quality", "Practical Design", "Great Value"],
                material_guess="",
                color_scheme="",
                suggested_scene="home setting",
            )

    def generate_image(
        self,
        reference: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        style_strength: float = 0.3,
    ) -> ImageResult:
        """
        生成图片
        
        Args:
            reference: 参考图片
            prompt: 生成提示词
            negative_prompt: 负向提示词
            aspect_ratio: 宽高比 (1:1, 4:3, 16:9 等)
            resolution: 分辨率 (1K, 2K, 4K) - 仅 Pro 支持 2K/4K
            style_strength: 风格强度
        """
        # 压缩参考图
        buf = io.BytesIO()
        img = reference.copy()
        if img.width > 1024 or img.height > 1024:
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        img.save(buf, format="PNG", optimize=True)
        img_data = buf.getvalue()
        
        # 构建完整提示词
        full_prompt = f"""
Based on the reference product image, create a new image following these requirements:

CRITICAL RULES:
- Keep the EXACT same product from the reference image
- Only modify: background, lighting, composition, presentation style
- Style transformation level: {style_strength} (0=minimal change, 1=creative)

REQUIREMENTS:
{prompt}

MUST AVOID:
{negative_prompt}

Generate a professional, high-quality image of the SAME product with the new styling."""

        # 配置生成参数
        image_config_params = {"aspect_ratio": aspect_ratio}
        
        # Pro 模型支持更高分辨率
        if self.is_pro and resolution in ["2K", "4K"]:
            image_config_params["image_size"] = resolution
        
        def call_api():
            cfg = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(**image_config_params),
            )
            return self.client.models.generate_content(
                model=self.model,
                contents=[types.Part.from_bytes(data=img_data, mime_type="image/png"), full_prompt],
                config=cfg,
            )
        
        resp = self._retry(call_api)
        
        # 提取图片
        result_img, thinking_imgs = self._extract_images(resp)
        
        if result_img is None:
            raise RuntimeError("模型未返回图片，请检查输入或稍后重试")
        
        return ImageResult(image=result_img, raw_response=resp, thinking_images=thinking_imgs)

    def generate_text_to_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
    ) -> ImageResult:
        """
        纯文本生成图片 (无参考图)
        """
        image_config_params = {"aspect_ratio": aspect_ratio}
        if self.is_pro and resolution in ["2K", "4K"]:
            image_config_params["image_size"] = resolution
        
        def call_api():
            cfg = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(**image_config_params),
            )
            return self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=cfg,
            )
        
        resp = self._retry(call_api)
        result_img, thinking_imgs = self._extract_images(resp)
        
        if result_img is None:
            raise RuntimeError("模型未返回图片")
        
        return ImageResult(image=result_img, raw_response=resp, thinking_images=thinking_imgs)

    def _extract_images(self, resp: Any) -> tuple:
        """
        从响应中提取图片
        返回: (最终图片, Thinking过程图片列表)
        """
        final_image = None
        thinking_images = []
        
        try:
            # 遍历所有 parts
            for part in getattr(resp, "parts", []) or []:
                # 检查是否是 thinking 阶段的图片
                is_thought = getattr(part, "thought", False)
                
                # 尝试获取图片
                img = None
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    try:
                        img = Image.open(io.BytesIO(inline.data)).convert("RGB")
                    except Exception:
                        pass
                elif hasattr(part, "as_image"):
                    try:
                        img = part.as_image().convert("RGB")
                    except Exception:
                        pass
                
                if img:
                    if is_thought:
                        thinking_images.append(img)
                    else:
                        final_image = img  # 最后一个非 thought 图片是最终结果
            
            # 如果没找到，尝试从 candidates 中提取
            if final_image is None:
                candidates = getattr(resp, "candidates", None)
                if candidates:
                    for cand in candidates:
                        content = getattr(cand, "content", None)
                        if not content:
                            continue
                        for part in getattr(content, "parts", []) or []:
                            inline = getattr(part, "inline_data", None)
                            if inline and getattr(inline, "data", None):
                                try:
                                    final_image = Image.open(io.BytesIO(inline.data)).convert("RGB")
                                except Exception:
                                    pass
                            elif hasattr(part, "as_image"):
                                try:
                                    final_image = part.as_image().convert("RGB")
                                except Exception:
                                    pass
        except Exception:
            pass
        
        return final_image, thinking_images
