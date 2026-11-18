import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from aspect_analysis import analyze_aspects
from preprocessing import clean_review, rating_to_sentiment


def test_clean_review_preserves_negation():
    text = "<b>NOT</b> good http://example.com !!!"
    cleaned = clean_review(text)
    assert "not" in cleaned
    assert "http" not in cleaned


def test_rating_label_strategy():
    assert rating_to_sentiment(1) == "Negative"
    assert rating_to_sentiment(3) == "Neutral"
    assert rating_to_sentiment(5) == "Positive"


def test_aspect_extraction():
    result = analyze_aspects("Excellent camera but terrible battery life.")
    assert "battery life" in result
    assert result["battery life"]["sentiment"] in {"Positive", "Negative", "Neutral"}
