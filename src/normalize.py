import re
import unicodedata
from typing import Dict, Iterable


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_text(text: str) -> str:
    text = strip_accents(text).lower()
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_title(title: str) -> str:
    return normalize_text(title)


def canonicalize_venue(venue: str, aliases: Dict[str, str]) -> str:
    norm = normalize_text(venue)
    if not norm:
        return ""
    if norm in aliases:
        return aliases[norm]
    return norm


def build_alias_map(raw_aliases: Dict[str, str]) -> Dict[str, str]:
    alias_map: Dict[str, str] = {}
    for alias, canonical in raw_aliases.items():
        alias_map[normalize_text(alias)] = normalize_text(canonical)
    return alias_map


def normalize_whitelist(journals: Iterable[str], aliases: Dict[str, str]) -> set[str]:
    normalized = set()
    for journal in journals:
        normalized.add(canonicalize_venue(journal, aliases))
    return normalized
