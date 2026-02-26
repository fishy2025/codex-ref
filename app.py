from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.agent import PaperSearchAgent, paper_to_api_payload

app = FastAPI(title="Microalgae Paper Search")
templates = Jinja2Templates(directory="templates")
agent = PaperSearchAgent()

DEFAULTS = {
    "topic": "microalgae",
    "days": 30,
    "max_results": 20,
    "include_preprints": False,
}


def _render_context(extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = {**DEFAULTS, "papers": [], "error": None, "sources_used": []}
    if extra:
        context.update(extra)
    return context


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, **_render_context()})


@app.post("/search", response_class=HTMLResponse)
def run_search(
    request: Request,
    topic: str = Form(DEFAULTS["topic"]),
    days: int = Form(DEFAULTS["days"]),
    max_results: int = Form(DEFAULTS["max_results"]),
    include_preprints: bool = Form(False),
):
    result = agent.search(topic=topic, days=days, max_results=max_results, include_preprints=include_preprints)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            **_render_context(
                {
                    "topic": topic,
                    "days": days,
                    "max_results": max_results,
                    "include_preprints": include_preprints,
                    "papers": result.papers,
                    "error": result.error,
                    "sources_used": result.sources_used,
                    "source_unavailable": result.source_unavailable,
                }
            ),
        },
    )


@app.get("/api/search")
def api_search(
    topic: str = Query(DEFAULTS["topic"]),
    days: int = Query(DEFAULTS["days"], ge=1, le=365),
    max_results: int = Query(DEFAULTS["max_results"], alias="max", ge=1, le=100),
    include_preprints: bool = Query(DEFAULTS["include_preprints"]),
):
    result = agent.search(topic=topic, days=days, max_results=max_results, include_preprints=include_preprints)
    return {
        "query": {
            "topic": topic,
            "days": days,
            "max_results": max_results,
            "include_preprints": include_preprints,
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sources_used": result.sources_used,
        "source_unavailable": result.source_unavailable,
        "error": result.error,
        "papers": [paper_to_api_payload(p) for p in result.papers],
    }
