from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.clients.arxiv import ArxivClient
from src.config_loader import load_simple_yaml
from src.clients.crossref import CrossrefClient, CrossrefError
from src.normalize import build_alias_map, canonicalize_venue, normalize_title, normalize_whitelist
from src.scoring import combined_score

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"


@dataclass
class SearchResult:
    papers: List[Dict[str, Any]]
    sources_used: List[str]
    source_unavailable: bool = False
    error: str | None = None


class PaperSearchAgent:
    def __init__(self) -> None:
        self.whitelist = self._load_yaml("journals_whitelist.yaml")
        aliases_raw = self._load_yaml("journal_aliases.yaml")
        self.alias_map = build_alias_map(aliases_raw)
        self.whitelist_norm = normalize_whitelist(self.whitelist, self.alias_map)
        self.keyword_weights = self._load_yaml("keyword_weights.yaml")
        self.crossref = CrossrefClient()
        self.arxiv = ArxivClient()

    def _load_yaml(self, filename: str):
        return load_simple_yaml(CONFIG_DIR / filename)

    def search(self, topic: str, days: int = 30, max_results: int = 20, include_preprints: bool = False) -> SearchResult:
        papers: List[Dict[str, Any]] = []
        sources: List[str] = []
        source_unavailable = False
        error = None

        try:
            crossref_items = self.crossref.search(topic, days, max_results * 3)
            sources.append("crossref")
            papers.extend(self._filter_whitelist(crossref_items))
        except CrossrefError as exc:
            source_unavailable = True
            error = f"Crossref unavailable: {exc}"

        if include_preprints:
            arxiv_items = self.arxiv.search(topic, days, max_results)
            if arxiv_items:
                sources.append("arxiv")
                papers.extend(arxiv_items)

        deduped = self._dedupe(papers)
        scored = self._score_papers(deduped, days)
        scored.sort(key=lambda p: (p["score"], p.get("published_date") or ""), reverse=True)
        return SearchResult(papers=scored[:max_results], sources_used=sources, source_unavailable=source_unavailable, error=error)

    def _filter_whitelist(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = []
        for p in papers:
            canonical = canonicalize_venue(p.get("venue", ""), self.alias_map)
            if canonical in self.whitelist_norm:
                p["venue"] = p.get("venue") or canonical
                filtered.append(p)
        return filtered

    @staticmethod
    def _metadata_richness(paper: Dict[str, Any]) -> int:
        return int(bool(paper.get("abstract_snippet"))) + int(bool(paper.get("doi"))) + int(bool(paper.get("authors")))

    def _dedupe(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        best: Dict[str, Dict[str, Any]] = {}
        for paper in papers:
            key = normalize_title(paper.get("title", ""))
            if not key:
                continue
            if key not in best or self._metadata_richness(paper) > self._metadata_richness(best[key]):
                best[key] = paper
        return list(best.values())

    def _score_papers(self, papers: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        out = []
        for paper in papers:
            pub_date = None
            if paper.get("published_date"):
                try:
                    pub_date = date.fromisoformat(paper["published_date"])
                except ValueError:
                    pub_date = None
            text = f"{paper.get('title', '')} {paper.get('abstract_snippet', '')}"
            score, matched_keywords = combined_score(text, pub_date, days, self.keyword_weights)
            paper["score"] = score
            paper["matched_keywords"] = matched_keywords
            out.append(paper)
        return out


def paper_to_api_payload(paper: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": paper.get("title"),
        "url": paper.get("url"),
        "doi": paper.get("doi"),
        "venue": paper.get("venue"),
        "published_date": paper.get("published_date"),
        "authors": paper.get("authors") or [],
        "abstract_snippet": paper.get("abstract_snippet") or "",
        "score": paper.get("score", 0.0),
        "matched_keywords": paper.get("matched_keywords") or [],
    }
