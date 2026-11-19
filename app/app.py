import sys
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from aspect_analysis import analyze_aspects
from preprocessing import clean_review
from predict import predict_review

app = Flask(__name__, template_folder="templates", static_folder="static")

DATA_PATH = ROOT / "data" / "processed" / "processed_reviews.csv"
RESULT_PATH = ROOT / "reports" / "model_evaluation_results.csv"


def safe_float(value):
    try:
        number = float(value)
        return number if pd.notna(number) else None
    except (TypeError, ValueError):
        return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    body = request.get_json(silent=True) or {}
    text = str(body.get("text", "")).strip()
    rating = body.get("rating")
    if not text:
        return jsonify({"error": "Please enter review text."}), 400

    sentiment, confidence, emotion = predict_review(text)
    result = {
        "sentiment": sentiment,
        "confidence": safe_float(confidence),
        "emotion": emotion,
        "aspects": analyze_aspects(text),
    }

    if rating not in (None, "", 0):
        try:
            rating_value = int(rating)
            rating_sentiment = "Negative" if rating_value <= 2 else "Neutral" if rating_value == 3 else "Positive"
            result["rating_sentiment"] = rating_sentiment
            result["rating_match"] = rating_sentiment == sentiment
        except (TypeError, ValueError):
            pass

    return jsonify(result)


@app.route("/api/aspects", methods=["POST"])
def aspects():
    body = request.get_json(silent=True) or {}
    text = str(body.get("text", "")).strip()
    if not text:
        return jsonify({"error": "Please enter review text."}), 400
    return jsonify({"aspects": analyze_aspects(text)})


@app.route("/api/bulk", methods=["POST"])
def bulk():
    uploaded = request.files.get("file")
    if uploaded is None:
        return jsonify({"error": "Please upload a CSV file."}), 400

    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        return jsonify({"error": f"Could not read CSV: {exc}"}), 400

    text_col = "text" if "text" in df.columns else "review_text" if "review_text" in df.columns else None
    if text_col is None:
        return jsonify({"error": "CSV must contain a 'text' or 'review_text' column."}), 400

    df["clean_text"] = df[text_col].fillna("").apply(clean_review)
    predictions = [predict_review(value) for value in df["clean_text"]]
    df["Predicted_Sentiment"] = [item[0] for item in predictions]
    df["Confidence"] = [safe_float(item[1]) for item in predictions]
    df["Detected_Emotion"] = [item[2] for item in predictions]

    summary = df["Predicted_Sentiment"].value_counts().to_dict()
    preview = df.head(100).where(pd.notna(df.head(100)), None).to_dict(orient="records")
    return jsonify({"summary": summary, "total": len(df), "preview": preview})


@app.route("/api/analytics")
def analytics():
    if not DATA_PATH.exists():
        return jsonify({"error": "Processed dataset not found. Run src/train_models.py first."}), 404

    df = pd.read_csv(DATA_PATH)
    sentiment_counts = df["sentiment"].value_counts().to_dict() if "sentiment" in df else {}
    rating = pd.to_numeric(df["rating"], errors="coerce") if "rating" in df else pd.Series(dtype=float)

    product_col = "parent_asin" if "parent_asin" in df.columns else "asin" if "asin" in df.columns else None
    products = []
    if product_col:
        products = sorted(df[product_col].dropna().astype(str).unique().tolist())[:500]

    return jsonify({
        "total": len(df),
        "sentiment": sentiment_counts,
        "averageRating": round(rating.mean(), 2) if not rating.empty else None,
        "products": products,
    })


@app.route("/api/comparison", methods=["POST"])
def comparison():
    body = request.get_json(silent=True) or {}
    selected = body.get("products", [])
    if not DATA_PATH.exists():
        return jsonify({"error": "Processed dataset not found."}), 404

    df = pd.read_csv(DATA_PATH)
    product_col = "parent_asin" if "parent_asin" in df.columns else "asin" if "asin" in df.columns else None
    if not product_col:
        return jsonify({"error": "No product identifier is available."}), 400

    subset = df[df[product_col].astype(str).isin([str(value) for value in selected])]
    comparison_rows = subset.groupby(product_col).agg(
        Reviews=("clean_text", "count"),
        Average_Rating=("rating", "mean")
    ).reset_index()
    comparison_rows["Average_Rating"] = comparison_rows["Average_Rating"].round(2)

    sentiment_rows = []
    for product, group in subset.groupby(product_col):
        counts = group["sentiment"].value_counts(normalize=True).mul(100).round(1)
        for sentiment, percentage in counts.items():
            sentiment_rows.append({"product": str(product), "sentiment": sentiment, "percentage": float(percentage)})

    return jsonify({
        "products": comparison_rows.where(pd.notna(comparison_rows), None).to_dict(orient="records"),
        "sentiment": sentiment_rows,
    })


@app.route("/api/model")
def model_results():
    if not RESULT_PATH.exists():
        return jsonify({"error": "Evaluation files not found. Run src/train_models.py first."}), 404

    results = pd.read_csv(RESULT_PATH)
    return jsonify({"results": results.where(pd.notna(results), None).to_dict(orient="records")})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
