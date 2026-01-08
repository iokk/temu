"""
TEMU 智能出图系统 - 提示词模板系统
核心作者: 企鹅

定义各种电商图片类型的提示词模板
"""
from typing import Dict


# ============ 模板定义 ============
TEMPLATES: Dict[str, Dict[str, str]] = {
    "C1": {
        "name": "主卖点图",
        "default": """Product hero shot for e-commerce:
Product: {product_name} ({product_type}), material: {material}

Layout: Square 1:1, clean gradient background (white to light gray)
Product: Centered, occupying 60-70% of frame, slight 15° angle for dimension

Key selling points to highlight:
{selling_points}

Style: Professional product photography, soft studio lighting, subtle shadow
Text: Add headline "{title}" in modern sans-serif font at top

Output: Clean, premium e-commerce main image""",
    },
    "C2": {
        "name": "场景图",
        "default": """Lifestyle scene product photography:
Product: {product_name} ({product_type}), material: {material}

Scene: {scene} setting with natural lighting
Product: Integrated naturally into scene, in-use or ready-to-use position

Atmosphere: Warm, inviting, realistic lifestyle moment
Composition: Rule of thirds, shallow depth of field

Key features to show:
{selling_points}

Style: Natural lifestyle photography, relatable and authentic

Output: Contextual scene showing product in real-life use""",
    },
    "C3": {
        "name": "细节图",
        "default": """Product detail close-up photography:
Product: {product_name} ({product_type}), material: {material}

Focus area: {detail_focus}
Angle: Extreme close-up, macro perspective

Lighting: Directional light to emphasize texture and craftsmanship
Composition: Fill frame with detail area, shallow DoF

Show clearly:
{selling_points}

Style: High-resolution macro photography, emphasize quality

Output: Detail shot showcasing craftsmanship and material quality""",
    },
    "C4": {
        "name": "对比图",
        "default": """Product comparison visualization:
Product: {product_name} ({product_type}), material: {material}

Layout: Split screen or before/after style comparison
Comparison points:
{compare_points}

Left/Before: Standard or competitor alternative
Right/After: This product showing improvements

Annotations: Simple visual indicators (arrows, highlights)

Style: Clear, educational, side-by-side comparison

Output: Comparison image highlighting product advantages""",
    },
    "C5": {
        "name": "规格图",
        "default": """Product specifications infographic:
Product: {product_name} ({product_type}), material: {material}

Layout: Clean infographic style with product centered
Product: Professional angle, white background

Specifications to display:
- Dimensions: {dimensions}
- Material: {material}
- Key features:
{selling_points}

Style: Technical infographic, clear typography, minimalist icons

Output: Professional spec sheet with product and key information""",
    },
}


# ============ 模板标签 ============
TEMPLATE_LABELS: Dict[str, str] = {tid: info["name"] for tid, info in TEMPLATES.items()}


def get_template(template_id: str) -> str:
    """
    获取指定模板的默认提示词
    
    Args:
        template_id: 模板 ID (C1, C2, C3, C4, C5)
        
    Returns:
        模板提示词
    """
    if template_id not in TEMPLATES:
        raise ValueError(f"未知模板ID: {template_id}")
    return TEMPLATES[template_id]["default"]


def format_template(template_id: str, **kwargs) -> str:
    """
    格式化模板，填入变量
    
    Args:
        template_id: 模板 ID
        **kwargs: 模板变量
        
    Returns:
        格式化后的提示词
    """
    template = get_template(template_id)
    return template.format(**kwargs)
