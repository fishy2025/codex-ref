from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import date
from typing import Any, Dict, List


CROSSREF_URL = "https://api.crossref.org/works"


class CrossrefError(Exception):
    pass


class CrossrefClient:
    def __init__(self, mailto: str = "local-test@example.com", timeout: int = 10, retries: int = 2):
        self.timeout = timeout
        self.retries = retries
        self.user_agent = f"microalgae-paper-search/1.0 (mailto:{mailto})"

    def search(self, topic: str, days: int, max_results: int) -> List[Dict[str, Any]]:
        today = date.today()
        from_date = today.fromordinal(today.toordinal() - days)
        params = {
            "query": topic,
            "rows": max_results,
            "filter": f"from-pub-date:{from_date.isoformat()},until-pub-date:{today.isoformat()}",
            "sort": "published",
            "order": "desc",
        }
        url = f"{CROSSREF_URL}?{urllib.parse.urlencode(params)}"

        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8")
                items = json.loads(body).get("message", {}).get("items", [])
                return [self._parse_item(i) for i in items]
            except Exception as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(0.4)
        raise CrossrefError(str(last_error))

    @staticmethod
    def _parse_date_parts(item: Dict[str, Any]) -> str | None:
        for key in ("published-print", "published-online", "issued", "created"):
            parts = item.get(key, {}).get("date-parts", [])
            if parts and parts[0]:
                d = parts[0]
                year = d[0]
                month = d[1] if len(d) > 1 else 1
                day = d[2] if len(d) > 2 else 1
                return f"{year:04d}-{month:02d}-{day:02d}"
        return None

    @staticmethod
    def _parse_item(item: Dict[str, Any]) -> Dict[str, Any]:
        title = (item.get("title") or [""])[0]
        abstract = item.get("abstract") or ""
        if abstract:
            abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "")
        doi = item.get("DOI")
        url = item.get("URL")
        container = (item.get("container-title") or [""])[0]
        authors = []
        for a in item.get("author", []):
            full_name = " ".join(x for x in [a.get("given"), a.get("family")] if x)
            if full_name:
                authors.append(full_name)
        return {
            "title": title,
            "url": url,
            "doi": doi,
            "venue": container,
            "published_date": CrossrefClient._parse_date_parts(item),
            "authors": authors,
            "abstract_snippet": abstract[:400],
            "source": "crossref",
            "is_preprint": False,
        }
