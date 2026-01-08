"""
TEMU 智能出图系统 - 提示词模板
核心作者: 企鹅
"""
from typing import Dict


TEMPLATES: Dict[str, Dict[str, str]] = {
    "C1": {
        "name": "主卖点图",
        "default": """Product hero shot for e-commerce:
Product: {product_name} ({product_type}), material: {material}

Layout: Square 1:1, clean gradient background (white to light gray)
Product: Centered, occupying 60-70% of frame, slight 15° angle

Key selling points:
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
Product: Integrated naturally into scene, in-use position

Atmosphere: Warm, inviting, realistic lifestyle
Composition: Rule of thirds, shallow depth of field

Key features:
{selling_points}

Style: Natural lifestyle photography, authentic

Output: Contextual scene showing product in real-life use""",
    },
    "C3": {
        "name": "细节图",
        "default": """Product detail close-up:
Product: {product_name} ({product_type}), material: {material}

Focus: {detail_focus}
Angle: Extreme close-up, macro perspective

Lighting: Directional light to emphasize texture
Composition: Fill frame with detail, shallow DoF

Show:
{selling_points}

Style: High-resolution macro photography

Output: Detail shot showcasing craftsmanship""",
    },
    "C4": {
        "name": "对比图",
        "default": """Product comparison:
Product: {product_name} ({product_type}), material: {material}

Layout: Split screen or before/after style
Comparison:
{compare_points}

Left: Standard alternative
Right: This product showing improvements

Annotations: Simple visual indicators

Style: Clear, educational comparison

Output: Comparison highlighting advantages""",
    },
    "C5": {
        "name": "规格图",
        "default": """Product specifications infographic:
Product: {product_name} ({product_type}), material: {material}

Layout: Clean infographic, product centered
Background: White

Specifications:
- Dimensions: {dimensions}
- Material: {material}
- Features:
{selling_points}

Style: Technical infographic, clear typography

Output: Professional spec sheet""",
    },
}

TEMPLATE_LABELS: Dict[str, str] = {tid: info["name"] for tid, info in TEMPLATES.items()}


def get_template(template_id: str) -> str:
    """获取模板"""
    if template_id not in TEMPLATES:
        raise ValueError(f"未知模板: {template_id}")
    return TEMPLATES[template_id]["default"]


def format_template(template_id: str, **kwargs) -> str:
    """格式化模板"""
    return get_template(template_id).format(**kwargs)
