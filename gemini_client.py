"""
TEMU 智能出图系统 - Gemini AI 客户端
核心作者: 企鹅
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
class GeminiImageResult:
    """图片生成结果"""
    image: Image.Image
    raw_response: Any


@dataclass
class ProductAnalysis:
    """AI 分析产品图片后提取的信息"""
    product_description: str
    key_features: List[str]
    material_guess: str
    color_scheme: str
    suggested_scene: str


class GeminiImageClient:
    """Gemini 图片处理客户端"""

    def __init__(self, api_key: str, model: str, max_retries: int = 3):
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.client = genai.Client(api_key=api_key)

    def _retry_with_backoff(self, func, *args, **kwargs):
        """带退避的重试"""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                err_msg = str(e).lower()
                retryable = any(x in err_msg for x in ["timeout", "rate", "503", "429", "retry"])
                if retryable and attempt < self.max_retries - 1:
                    time.sleep((2 ** attempt) + 1)
                    continue
                break
        raise last_error

    def analyze_product_image(self, image: Image.Image) -> ProductAnalysis:
        """分析产品图片"""
        buffered = io.BytesIO()
        img = image.copy()
        if img.width > 1024 or img.height > 1024:
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        img.save(buffered, format="PNG", optimize=True)
        img_data = buffered.getvalue()
        
        prompt = """Analyze this product image and return JSON only:
{
    "product_description": "Brief description",
    "key_features": ["Feature 1", "Feature 2", "Feature 3"],
    "material_guess": "Material",
    "color_scheme": "Colors",
    "suggested_scene": "Usage scenario"
}
Return ONLY JSON, no other text."""
        
        def do_analysis():
            cfg = types.GenerateContentConfig(response_modalities=["TEXT"])
            return self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[types.Part.from_bytes(data=img_data, mime_type="image/png"), prompt],
                config=cfg,
            )
        
        try:
            resp = self._retry_with_backoff(do_analysis)
            text = resp.text.strip() if resp.text else ""
            
            # 清理 markdown
            for mark in ["```json", "```"]:
                text = text.replace(mark, "")
            text = text.strip()
            
            data = json.loads(text)
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

    def generate_image_from_reference(
        self,
        reference_image: Image.Image,
        prompt: str,
        negative_prompt: str,
        style_strength: float = 0.3
    ) -> GeminiImageResult:
        """基于参考图生成新图片"""
        buffered = io.BytesIO()
        img = reference_image.copy()
        if img.width > 1024 or img.height > 1024:
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        img.save(buffered, format="PNG", optimize=True)
        img_data = buffered.getvalue()
        
        full_prompt = f"""
CRITICAL: Keep the EXACT product from reference image.
Only modify: background, lighting, composition.
Style strength: {style_strength}

REQUIREMENTS:
{prompt}

AVOID:
{negative_prompt}

Generate the SAME product with new styling."""
        
        def do_generation():
            cfg = types.GenerateContentConfig(response_modalities=["IMAGE"])
            return self.client.models.generate_content(
                model=self.model,
                contents=[types.Part.from_bytes(data=img_data, mime_type="image/png"), full_prompt],
                config=cfg,
            )
        
        resp = self._retry_with_backoff(do_generation)
        img = self._extract_first_image(resp)
        
        if img is None:
            raise RuntimeError("模型未返回图片，请检查输入或稍后重试")
        
        return GeminiImageResult(image=img, raw_response=resp)

    @staticmethod
    def _extract_first_image(resp: Any) -> Optional[Image.Image]:
        """提取图片"""
        try:
            candidates = getattr(resp, "candidates", None)
            if candidates:
                for cand in candidates:
                    content = getattr(cand, "content", None)
                    if not content:
                        continue
                    parts = getattr(content, "parts", None) or []
                    for part in parts:
                        inline = getattr(part, "inline_data", None)
                        if inline and getattr(inline, "data", None):
                            return Image.open(io.BytesIO(inline.data)).convert("RGB")
                        if hasattr(part, "as_image"):
                            try:
                                return part.as_image().convert("RGB")
                            except Exception:
                                pass
        except Exception:
            pass
        
        try:
            parts = getattr(resp, "parts", None) or []
            for part in parts:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    return Image.open(io.BytesIO(inline.data)).convert("RGB")
        except Exception:
            pass
        
        return None
