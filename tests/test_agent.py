from src.agent import PaperSearchAgent


def test_dedupe_prefers_richer_metadata():
    agent = PaperSearchAgent()
    papers = [
        {
            "title": "Microalgae for wastewater",
            "abstract_snippet": "",
            "doi": None,
            "authors": [],
        },
        {
            "title": "Microalgae for wastewater!",
            "abstract_snippet": "Has abstract",
            "doi": "10.1/abc",
            "authors": ["A B"],
        },
    ]
    deduped = agent._dedupe(papers)
    assert len(deduped) == 1
    assert deduped[0]["doi"] == "10.1/abc"


def test_whitelist_alias_match():
    agent = PaperSearchAgent()
    papers = [{"venue": "Environ. Sci. Technol.", "title": "t"}]
    filtered = agent._filter_whitelist(papers)
    assert len(filtered) == 1
