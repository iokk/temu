"""
TEMU 智能出图系统 - Gemini AI 客户端
核心作者: 企鹅

封装 Gemini AI 的图片分析和图生图功能
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, List
from PIL import Image
import io
import json

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
    product_description: str  # 产品详细描述
    key_features: List[str]   # 3-5个核心特征/卖点
    material_guess: str       # 推断的材质
    color_scheme: str         # 主色调
    suggested_scene: str      # 建议的使用场景


class GeminiImageClient:
    """
    Gemini 图片处理客户端
    
    功能:
    - 图片分析（提取产品特征）
    - 图生图（基于原图优化）
    """

    def __init__(self, api_key: str, model: str):
        """
        初始化客户端
        
        Args:
            api_key: Gemini API Key
            model: 使用的模型名称
        """
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def analyze_product_image(self, image: Image.Image) -> ProductAnalysis:
        """
        使用 Gemini Vision 分析产品图片，提取关键信息
        
        Args:
            image: 产品图片
            
        Returns:
            产品分析结果
        """
        # 转换图片为字节
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_data = buffered.getvalue()
        
        prompt = """
Please analyze this product image and provide the following information in JSON format:

{
    "product_description": "A clear, detailed description of the product (1-2 sentences)",
    "key_features": ["Feature 1", "Feature 2", "Feature 3"],  // 3-5 selling points based on what you see
    "material_guess": "The material the product appears to be made of",
    "color_scheme": "Main colors of the product",
    "suggested_scene": "Best usage scenario for this product (e.g., kitchen, living room, office)"
}

Focus on:
1. What makes this product special or appealing
2. Practical features visible in the image
3. Quality indicators you can see
4. Natural, authentic selling points (NOT generic phrases like "Premium Quality")

Return ONLY the JSON, no other text.
"""
        
        cfg = types.GenerateContentConfig(
            response_modalities=["TEXT"],
        )
        
        resp = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",  # 使用 Vision 模型
            contents=[
                types.Part.from_bytes(data=img_data, mime_type="image/png"),
                prompt,
            ],
            config=cfg,
        )
        
        # 解析 JSON 响应
        response_text = resp.text.strip()
        
        # 移除可能的 markdown 代码块标记
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        try:
            data = json.loads(response_text)
            return ProductAnalysis(
                product_description=data.get("product_description", ""),
                key_features=data.get("key_features", [])[:5],  # 最多5个
                material_guess=data.get("material_guess", ""),
                color_scheme=data.get("color_scheme", ""),
                suggested_scene=data.get("suggested_scene", "home setting"),
            )
        except json.JSONDecodeError:
            # 如果解析失败，返回默认值
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
        """
        基于参考图生成新图片（图生图）
        
        Args:
            reference_image: 原始商品图片
            prompt: 生成提示词
            negative_prompt: 负向提示词
            style_strength: 风格强度 (0.0-1.0)，越小越接近原图
            
        Returns:
            生成结果
        """
        # 转换参考图片
        buffered = io.BytesIO()
        reference_image.save(buffered, format="PNG")
        img_data = buffered.getvalue()
        
        # 构建完整的 prompt，强调保持产品本身
        full_prompt = f"""
CRITICAL INSTRUCTIONS:
1. The reference image shows the ACTUAL PRODUCT that must be preserved
2. Keep the product's EXACT appearance: shape, design, details, features
3. Only modify: background, lighting, composition, and presentation style
4. Style strength: {style_strength} (0=identical to reference, 1=completely new)

REFERENCE IMAGE ANALYSIS:
- This is the exact product that must appear in the output
- Maintain its authentic look and all visible features
- Do not change the product design or add fictional elements

STYLING REQUIREMENTS:
{prompt}

NEGATIVE CONSTRAINTS (MUST FOLLOW):
{negative_prompt}

OUTPUT REQUIREMENT:
Generate an image where the SAME product from the reference appears with the new styling/background/composition described above.
"""
        
        cfg = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )

        resp = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(data=img_data, mime_type="image/png"),
                full_prompt,
            ],
            config=cfg,
        )

        img = self._extract_first_image(resp)
        if img is None:
            raise RuntimeError("模型返回未包含图片数据（可能被阻止或仅返回文本）")

        return GeminiImageResult(image=img, raw_response=resp)

    @staticmethod
    def _extract_first_image(resp: Any) -> Optional[Image.Image]:
        """
        兼容式提取图片
        
        Args:
            resp: Gemini API 响应
            
        Returns:
            提取的图片，如果没有则返回 None
        """
        # candidates -> content -> parts
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
                            b = inline.data
                            return Image.open(io.BytesIO(b)).convert("RGB")
                        if hasattr(part, "as_image"):
                            try:
                                return part.as_image().convert("RGB")
                            except Exception:
                                pass
        except Exception:
            pass

        # resp.parts 兜底
        try:
            parts = getattr(resp, "parts", None) or []
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

        return None
