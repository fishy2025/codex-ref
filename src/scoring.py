from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

from src.normalize import normalize_text


DEFAULT_W_RECENCY = 0.35
DEFAULT_W_KEYWORD = 0.65


def recency_score(published_date: date | None, days: int) -> float:
    if not published_date:
        return 0.0
    age = (date.today() - published_date).days
    if age < 0:
        age = 0
    if age >= days:
        return 0.0
    return max(0.0, 1 - (age / max(days, 1)))


def keyword_score(text: str, keyword_weights: Dict[str, float]) -> Tuple[float, List[str]]:
    normalized = normalize_text(text)
    total_weight = sum(keyword_weights.values()) or 1.0
    score = 0.0
    matched: List[str] = []
    for keyword, weight in keyword_weights.items():
        kw_norm = normalize_text(keyword)
        if kw_norm and kw_norm in normalized:
            score += float(weight)
            matched.append(keyword)
    return min(1.0, score / total_weight), matched


def combined_score(
    text: str,
    published_date: date | None,
    days: int,
    keyword_weights: Dict[str, float],
    w_recency: float = DEFAULT_W_RECENCY,
    w_keyword: float = DEFAULT_W_KEYWORD,
) -> Tuple[float, List[str]]:
    r = recency_score(published_date, days)
    k, matched = keyword_score(text, keyword_weights)
    score = (w_recency * r) + (w_keyword * k)
    return round(score, 6), matched
