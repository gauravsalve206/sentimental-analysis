import html
import re

import pandas as pd

HTML_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+|www\.\S+")
SPECIAL_RE = re.compile(r"[^a-zA-Z0-9!?'.(),;:%-]+")
WHITESPACE_RE = re.compile(r"\s+")


def rating_to_sentiment(rating):
    if pd.isna(rating):
        return None
    rating = float(rating)
    if rating <= 2:
        return "Negative"
    if rating == 3:
        return "Neutral"
    return "Positive"


def clean_review(text):
    if pd.isna(text):
        return ""
    text = html.unescape(str(text).lower())
    text = HTML_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    text = SPECIAL_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def prepare_reviews(df):
    data = df.copy()
    data.columns = [str(column).strip().lower().replace(" ", "_") for column in data.columns]

    text_column = "text" if "text" in data else ("review_text" if "review_text" in data else None)
    if text_column is None:
        raise ValueError("CSV must contain 'text' or 'review_text'.")

    data["clean_text"] = data[text_column].apply(clean_review)
    data = data[data["clean_text"].str.len() > 0].copy()
    data = data.drop_duplicates(subset=["clean_text"], keep="first")

    if "rating" in data:
        data["rating"] = pd.to_numeric(data["rating"], errors="coerce")
        data["sentiment"] = data["rating"].apply(rating_to_sentiment)
    elif "sentiment" in data:
        data["sentiment"] = data["sentiment"].astype(str).str.title()
        data = data[data["sentiment"].isin(["Positive", "Negative", "Neutral"])]

    if "sentiment" not in data:
        raise ValueError("Data must contain 'rating' or 'sentiment'.")

    data = data.dropna(subset=["sentiment"])
    return data
