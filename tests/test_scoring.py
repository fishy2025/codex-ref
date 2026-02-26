from datetime import date, timedelta

from src.scoring import combined_score, recency_score


def test_recency_score_range():
    assert recency_score(date.today(), 30) == 1.0
    assert recency_score(date.today() - timedelta(days=30), 30) == 0.0


def test_combined_score_keyword_matching():
    weights = {"microalgae": 5, "nitrogen removal": 5, "wastewater": 4}
    text = "Microalgae for wastewater treatment with nitrogen removal"
    score, matched = combined_score(text, date.today(), 30, weights)
    assert score > 0.7
    assert set(matched) == {"microalgae", "nitrogen removal", "wastewater"}
