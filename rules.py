"""
TEMU 智能出图系统 - 规则引擎
核心作者: 企鹅

处理敏感词替换、禁用词检查、负向提示词构建
"""
import re
from typing import List, Tuple, Dict


# ============ 敏感词替换规则 ============
REPLACE_MAP: Dict[str, str] = {
    r"\bGold\b": "Golden",
    r"\bSilver\b": "Silvery",
    r"\bDiamond\b": "Crystal",
    r"\bPlatinum\b": "Metallic",
    r"\bRuby\b": "Faux Ruby",
    r"\bSapphire\b": "Artificial Stone",
    r"\bJade\b": "Artificial Stone",
}


# ============ 绝对禁止模式 ============
ABSOLUTE_BAN_PATTERNS: List[str] = [
    r"https?://",
    r"\bwww\.",
    r"\.com\b",
    r"\bqr\b",
    r"\bqrcode\b",
    r"\bbarcode\b",
    r"\bTemu\b",
]


# ============ 负向词库基础 ============
NEGATIVE_BASE: List[str] = [
    # 人物相关
    "no children, no baby, no kid, no infant",
    "no human face, no portrait, no full person, no nude, no sensitive body parts",
    # 政治/宗教
    "no political symbols, no flags, no propaganda",
    "no religious symbols, no blasphemy",
    # 仇恨/歧视/暴力
    "no hate, no discrimination, no violence, no torture, no kidnapping",
    # 导流/品牌侵权
    "no brand logo, no trademark, no watermark",
    "no QR code, no barcode, no URL, no website text, no social media handle",
]


def apply_replacements(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """
    替换敏感材质词：Gold->Golden 等
    
    Args:
        text: 输入文本
        
    Returns:
        (替换后的文本, 替换日志列表)
    """
    if not text:
        return text, []

    out = text
    logs: List[Tuple[str, str]] = []
    
    for pattern, repl in REPLACE_MAP.items():
        new_out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
        if new_out != out:
            logs.append((pattern, repl))
            out = new_out
            
    return out, logs


def check_absolute_bans(text: str) -> List[str]:
    """
    检查是否命中绝对禁用模式
    
    Args:
        text: 待检查的文本
        
    Returns:
        命中的模式列表
    """
    hits: List[str] = []
    if not text:
        return hits
        
    for p in ABSOLUTE_BAN_PATTERNS:
        if re.search(p, text, flags=re.IGNORECASE):
            hits.append(p)
            
    return hits


def build_negative_prompt(exclude_items: List[str], strict_mode: bool = True) -> str:
    """
    构建负向提示词
    
    Args:
        exclude_items: 用户指定的排除项
        strict_mode: 是否启用严格模式
        
    Returns:
        完整的负向提示词
    """
    neg = list(NEGATIVE_BASE)

    # 添加用户排除项
    for it in exclude_items or []:
        it = (it or "").strip()
        if it:
            neg.append(f"no {it}")

    # 严格模式额外约束
    if strict_mode:
        neg += [
            "no text, no labels, no typography",
            "no hands, no models",
            "no extra accessories, no props unrelated to the product",
            "clean background, studio product photo feel",
        ]

    # 去重（保持顺序）
    seen = set()
    dedup = []
    for x in neg:
        if x not in seen:
            seen.add(x)
            dedup.append(x)

    return ", ".join(dedup)
