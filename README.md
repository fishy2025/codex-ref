# Microalgae Paper Search (Local FastAPI App)

A local web test app for finding recent microalgae papers from top-journal venues, with keyword-weighted ranking and recency weighting.

## Features
- FastAPI + Jinja2 UI (`/` + `/search`).
- JSON API at `/api/search`.
- Crossref as primary source (polite User-Agent, timeout + retries).
- Optional arXiv preprints (only when enabled).
- Journal whitelist filtering with alias normalization.
- Weighted keyword scoring + recency blending.
- Deduplication by normalized title with richer-metadata preference.
- Graceful source error handling (`source_unavailable`).

## Local run
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```
Open http://127.0.0.1:8000

## API Example
```bash
curl "http://127.0.0.1:8000/api/search?topic=microalgae&days=30&max=20&include_preprints=false"
```

## Notes for Windows
- Works with standard Python 3.10+ on Windows PowerShell or CMD.
- If `uvicorn` command is not found, run `python -m uvicorn app:app --reload`.
