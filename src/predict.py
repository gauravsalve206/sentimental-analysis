import pickle
from pathlib import Path

from preprocessing import clean_review

BASE_DIR = Path(__file__).resolve().parent.parent


def load_model_artifacts():
    model_path = BASE_DIR / "models" / "trained_model.pkl"
    vectorizer_path = BASE_DIR / "models" / "tfidf_vectorizer.pkl"
    with model_path.open("rb") as handle:
        model = pickle.load(handle)
    with vectorizer_path.open("rb") as handle:
        vectorizer = pickle.load(handle)
    return model, vectorizer


def predict_review(text):
    model, vectorizer = load_model_artifacts()
    cleaned = clean_review(text)
    features = vectorizer.transform([cleaned])
    predicted = model.predict(features)[0]

    confidence = None
    if hasattr(model, "predict_proba"):
        confidence = float(model.predict_proba(features).max())
    elif hasattr(model, "decision_function"):
        scores = model.decision_function(features)
        confidence = float(max(0.0, min(1.0, (scores.max() + 1) / 2)))

    emotion = detect_emotion(cleaned)
    return predicted, confidence, emotion


def detect_emotion(text):
    text = text.lower()
    if any(word in text for word in ["angry", "rage", "hate", "furious"]):
        return "Angry"
    if any(word in text for word in ["disappointed", "let down", "expected", "worse"]):
        return "Disappointed"
    if any(word in text for word in ["frustrated", "annoying", "annoyed", "cannot", "won't"]):
        return "Frustrated"
    if any(word in text for word in ["satisfied", "happy", "excellent", "great", "perfect"]):
        return "Happy" if "happy" in text or "love" in text else "Satisfied"
    return "Neutral"
