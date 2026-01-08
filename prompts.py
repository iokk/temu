"""
TEMU 智能出图系统 V8.0
提示词模板 - 针对 Nano Banana Pro 优化
核心作者: 企鹅

变量说明:
    {product_name}    - 商品名称
    {product_type}    - 商品类型
    {material}        - 材质
    {selling_points}  - 卖点
    {scene}           - 使用场景
    {detail_focus}    - 细节重点
    {dimensions}      - 尺寸规格
    {title}           - 标题文字
    {style_prompt}    - 风格提示词 (来自预设)
"""

from typing import Dict, Any


# ==================== 模板信息 ====================
TEMPLATE_INFO: Dict[str, tuple] = {
    "C1": ("🌟", "主卖点图", "突出核心优势，吸引买家点击"),
    "C2": ("🏡", "场景图", "展示产品使用场景，建立情感连接"),
    "C3": ("🔍", "细节图", "展现工艺细节，提升购买信心"),
    "C4": ("⚖️", "对比图", "对比产品优势，突出价值"),
    "C5": ("📐", "规格图", "清晰展示产品参数信息"),
}


# ==================== 提示词模板 ====================
PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    
    "C1": {
        "name": "主卖点图",
        "prompt": """Create a professional e-commerce hero shot for: {product_name}

Product Details:
- Type: {product_type}
- Material: {material}
- Key Features: {selling_points}

Visual Requirements:
- Layout: Product centered, occupying 60-70% of frame
- Background: Clean gradient (white to light gray) or pure white
- Lighting: Professional studio lighting with soft shadows
- Angle: Slight 15° angle for dimension and appeal

Text Element (if applicable):
- Add headline "{title}" in modern, clean sans-serif font

Style: {style_prompt}

Output: High-quality, click-worthy e-commerce main image that attracts buyers.""",
    },
    
    "C2": {
        "name": "场景图",
        "prompt": """Create a lifestyle scene product photography for: {product_name}

Product Details:
- Type: {product_type}
- Material: {material}

Scene Requirements:
- Setting: {scene} with natural, warm lighting
- Product Position: Integrated naturally, in-use or ready-to-use
- Atmosphere: Warm, inviting, relatable lifestyle moment
- Composition: Rule of thirds, shallow depth of field

Key Features to Highlight:
{selling_points}

Style: {style_prompt}

Output: Authentic lifestyle image that connects emotionally with buyers.""",
    },
    
    "C3": {
        "name": "细节图",
        "prompt": """Create a product detail close-up for: {product_name}

Product Details:
- Type: {product_type}
- Material: {material}

Detail Requirements:
- Focus Area: {detail_focus}
- Perspective: Extreme close-up, macro view
- Lighting: Directional light emphasizing texture and craftsmanship
- Composition: Fill frame with detail, shallow depth of field

Quality Indicators to Show:
{selling_points}

Style: {style_prompt}

Output: High-resolution detail shot showcasing premium quality and craftsmanship.""",
    },
    
    "C4": {
        "name": "对比图",
        "prompt": """Create a product comparison visualization for: {product_name}

Product Details:
- Type: {product_type}
- Material: {material}

Comparison Layout:
- Format: Split screen or before/after style
- Left/Before: Generic or standard alternative (less appealing)
- Right/After: This product showing clear improvements

Comparison Points:
{selling_points}

Visual Elements:
- Simple annotations (arrows, highlights, icons)
- Clear visual distinction between options

Style: {style_prompt}

Output: Clear comparison image highlighting product advantages.""",
    },
    
    "C5": {
        "name": "规格图",
        "prompt": """Create a product specifications infographic for: {product_name}

Product Details:
- Type: {product_type}
- Material: {material}
- Dimensions: {dimensions}

Infographic Requirements:
- Layout: Clean, organized with product centered
- Background: Pure white
- Typography: Clear, legible text for all specifications

Specifications to Display:
{selling_points}

Visual Elements:
- Measurement lines and dimension indicators
- Minimalist icons for features
- Professional, technical aesthetic

Style: {style_prompt}

Output: Professional spec sheet providing all key information at a glance.""",
    },
}


# ==================== 辅助函数 ====================

def get_template_names() -> Dict[str, str]:
    return {tid: info["name"] for tid, info in PROMPT_TEMPLATES.items()}

def get_template_prompt(template_id: str) -> str:
    if template_id not in PROMPT_TEMPLATES:
        raise ValueError(f"未知模板: {template_id}")
    return PROMPT_TEMPLATES[template_id]["prompt"]

def get_template_info(template_id: str) -> tuple:
    return TEMPLATE_INFO.get(template_id, ("📷", template_id, ""))

def format_prompt(template_id: str, **kwargs) -> str:
    return get_template_prompt(template_id).format(**kwargs)

def get_all_templates() -> Dict[str, Any]:
    return {
        tid: {
            "name": info["name"],
            "prompt": info["prompt"],
            "icon": TEMPLATE_INFO.get(tid, ("📷",))[0],
            "description": TEMPLATE_INFO.get(tid, ("", "", ""))[2],
        }
        for tid, info in PROMPT_TEMPLATES.items()
    }
