"""
TEMU 智能出图系统 V8.0
规则引擎
核心作者: 企鹅
"""
import re
from typing import List, Tuple, Dict


REPLACE_RULES: Dict[str, str] = {
    r"\bGold\b": "Golden",
    r"\bSilver\b": "Silvery",
    r"\bDiamond\b": "Crystal",
    r"\bPlatinum\b": "Metallic",
}

BAN_PATTERNS: List[str] = [
    r"https?://", r"\bwww\.", r"\.com\b", r"\bqr\b", r"\bTemu\b",
]

NEGATIVE_BASE: List[str] = [
    "no children, no baby, no kid",
    "no human face, no portrait, no nude",
    "no political symbols, no religious symbols",
    "no brand logo, no trademark, no watermark",
    "no QR code, no barcode, no URL",
]


def apply_replacements(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    if not text:
        return text, []
    result, logs = text, []
    for pattern, repl in REPLACE_RULES.items():
        new = re.sub(pattern, repl, result, flags=re.IGNORECASE)
        if new != result:
            logs.append((pattern, repl))
            result = new
    return result, logs


def check_absolute_bans(text: str) -> List[str]:
    if not text:
        return []
    return [p for p in BAN_PATTERNS if re.search(p, text, flags=re.IGNORECASE)]


def build_negative_prompt(exclude_items: List[str], strict_mode: bool = True) -> str:
    negatives = list(NEGATIVE_BASE)
    for item in exclude_items or []:
        if item and item.strip():
            negatives.append(f"no {item.strip()}")
    if strict_mode:
        negatives.extend(["clean background", "no clutter"])
    return ", ".join(dict.fromkeys(negatives))
