"""
TEMU 智能出图系统 - 规则引擎
核心作者: 企鹅
"""
import re
from typing import List, Tuple, Dict


# 敏感词替换
REPLACE_MAP: Dict[str, str] = {
    r"\bGold\b": "Golden",
    r"\bSilver\b": "Silvery",
    r"\bDiamond\b": "Crystal",
    r"\bPlatinum\b": "Metallic",
    r"\bRuby\b": "Faux Ruby",
    r"\bSapphire\b": "Artificial Stone",
    r"\bJade\b": "Artificial Stone",
}

# 禁用模式
ABSOLUTE_BAN_PATTERNS: List[str] = [
    r"https?://",
    r"\bwww\.",
    r"\.com\b",
    r"\bqr\b",
    r"\bqrcode\b",
    r"\bbarcode\b",
    r"\bTemu\b",
]

# 负向词基础
NEGATIVE_BASE: List[str] = [
    "no children, no baby, no kid, no infant",
    "no human face, no portrait, no full person, no nude",
    "no political symbols, no flags, no propaganda",
    "no religious symbols",
    "no hate, no discrimination, no violence",
    "no brand logo, no trademark, no watermark",
    "no QR code, no barcode, no URL, no website text",
]


def apply_replacements(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    """替换敏感词"""
    if not text:
        return text, []
    
    out = text
    logs = []
    
    for pattern, repl in REPLACE_MAP.items():
        new_out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
        if new_out != out:
            logs.append((pattern, repl))
            out = new_out
    
    return out, logs


def check_absolute_bans(text: str) -> List[str]:
    """检查禁用模式"""
    if not text:
        return []
    
    return [p for p in ABSOLUTE_BAN_PATTERNS if re.search(p, text, flags=re.IGNORECASE)]


def build_negative_prompt(exclude_items: List[str], strict_mode: bool = True) -> str:
    """构建负向提示词"""
    neg = list(NEGATIVE_BASE)
    
    for it in exclude_items or []:
        it = (it or "").strip()
        if it:
            neg.append(f"no {it}")
    
    if strict_mode:
        neg.extend([
            "no text, no labels, no typography",
            "no hands, no models",
            "clean background, studio product photo",
        ])
    
    # 去重
    seen = set()
    return ", ".join(x for x in neg if not (x in seen or seen.add(x)))
