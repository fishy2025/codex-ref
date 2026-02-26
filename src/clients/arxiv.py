from __future__ import annotations

import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from typing import Any, Dict, List


ARXIV_URL = "http://export.arxiv.org/api/query"


class ArxivClient:
    def __init__(self, timeout: int = 10, retries: int = 2):
        self.timeout = timeout
        self.retries = retries
        self.user_agent = "microalgae-paper-search/1.0"

    def search(self, topic: str, days: int, max_results: int) -> List[Dict[str, Any]]:
        min_date = date.today() - timedelta(days=days)
        params = {
            "search_query": f"all:{topic}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = f"{ARXIV_URL}?{urllib.parse.urlencode(params)}"
        for attempt in range(self.retries + 1):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8")
                return self._parse_feed(body, min_date)
            except Exception:
                if attempt < self.retries:
                    time.sleep(0.4)
        return []

    @staticmethod
    def _parse_feed(xml_text: str, min_date: date) -> List[Dict[str, Any]]:
        root = ET.fromstring(xml_text)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        output = []
        for entry in root.findall("a:entry", ns):
            published = entry.findtext("a:published", default="", namespaces=ns)
            pub_date = published[:10]
            if pub_date and date.fromisoformat(pub_date) < min_date:
                continue
            title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
            summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
            url = entry.findtext("a:id", default="", namespaces=ns)
            authors = [a.findtext("a:name", default="", namespaces=ns) for a in entry.findall("a:author", ns)]
            output.append(
                {
                    "title": title,
                    "url": url,
                    "doi": None,
                    "venue": "arXiv",
                    "published_date": pub_date,
                    "authors": [a for a in authors if a],
                    "abstract_snippet": summary[:400],
                    "source": "arxiv",
                    "is_preprint": True,
                }
            )
        return output
