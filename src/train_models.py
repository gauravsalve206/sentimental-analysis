import json
import pickle
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from datasets import load_dataset
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import label_binarize
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from preprocessing import prepare_reviews, rating_to_sentiment


def download_and_save_sample(max_per_class=10000):
    raw_dir = ROOT / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    ds = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023",
        "raw_review_All_Beauty",
        trust_remote_code=True,
    )
    df = ds["full"].to_pandas()
    df["sentiment"] = df["rating"].apply(rating_to_sentiment)

    sample_parts = []
    for sentiment in ["Negative", "Neutral", "Positive"]:
        part = df[df["sentiment"] == sentiment]
        count = min(max_per_class, len(part))
        sample_parts.append(part.sample(n=count, random_state=42))

    sample = pd.concat(sample_parts).sample(frac=1, random_state=42).reset_index(drop=True)
    sample.to_csv(raw_dir / "amazon_all_beauty_sample.csv", index=False)
    return sample


def plot_confusion_matrix(cm, labels, title, path):
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.set_xticks(range(len(labels)), labels=labels)
    ax.set_yticks(range(len(labels)), labels=labels)
    ax.set_title(title)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    (ROOT / "models").mkdir(parents=True, exist_ok=True)
    (ROOT / "reports").mkdir(parents=True, exist_ok=True)

    raw_path = ROOT / "data" / "raw" / "amazon_all_beauty_sample.csv"
    if raw_path.exists():
        df = pd.read_csv(raw_path)
    else:
        df = download_and_save_sample()

    df = prepare_reviews(df)

    processed_dir = ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_dir / "processed_reviews.csv", index=False)

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"], df["sentiment"], test_size=0.2,
        random_state=42, stratify=df["sentiment"]
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True,
        max_features=50000,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "Multinomial Naive Bayes": MultinomialNB(),
        "Linear SVM": LinearSVC(class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=40, n_jobs=-1,
                                                class_weight="balanced", random_state=42),
    }

    labels = ["Negative", "Neutral", "Positive"]
    results = []
    fitted_models = {}

    for name, model in models.items():
        model.fit(X_train_tfidf, y_train)
        predictions = model.predict(X_test_tfidf)
        fitted_models[name] = model

        report = classification_report(y_test, predictions, labels=labels,
                                       output_dict=True, zero_division=0)
        row = {
            "model": name,
            "accuracy": accuracy_score(y_test, predictions),
            "precision_macro": precision_score(y_test, predictions, average="macro", zero_division=0),
            "recall_macro": recall_score(y_test, predictions, average="macro", zero_division=0),
            "f1_macro": f1_score(y_test, predictions, average="macro", zero_division=0),
            "precision_negative": report["Negative"]["precision"],
            "recall_negative": report["Negative"]["recall"],
            "f1_negative": report["Negative"]["f1-score"],
            "precision_neutral": report["Neutral"]["precision"],
            "recall_neutral": report["Neutral"]["recall"],
            "f1_neutral": report["Neutral"]["f1-score"],
            "precision_positive": report["Positive"]["precision"],
            "recall_positive": report["Positive"]["recall"],
            "f1_positive": report["Positive"]["f1-score"],
        }

        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_test_tfidf)
            binarized = label_binarize(y_test, classes=model.classes_)
            try:
                row["roc_auc_macro_ovr"] = roc_auc_score(binarized, proba,
                                                         average="macro", multi_class="ovr")
            except ValueError:
                row["roc_auc_macro_ovr"] = None
        elif hasattr(model, "decision_function"):
            row["roc_auc_macro_ovr"] = None
        else:
            row["roc_auc_macro_ovr"] = None

        results.append(row)

        cm = confusion_matrix(y_test, predictions, labels=labels)
        plot_confusion_matrix(cm, labels, f"{name} Confusion Matrix",
                              ROOT / "reports" / f"confusion_{name.lower().replace(' ', '_')}.png")

    results_df = pd.DataFrame(results).sort_values("f1_macro", ascending=False)
    results_df.to_csv(ROOT / "reports" / "model_evaluation_results.csv", index=False)
    results_df.to_csv(ROOT / "model_evaluation_results.csv", index=False)

    best_row = results_df.iloc[0]
    best_name = best_row["model"]
    best_model = fitted_models[best_name]

    with (ROOT / "models" / "trained_model.pkl").open("wb") as handle:
        pickle.dump(best_model, handle)
    with (ROOT / "models" / "tfidf_vectorizer.pkl").open("wb") as handle:
        pickle.dump(vectorizer, handle)

    metadata = {
        "dataset": "McAuley-Lab/Amazon-Reviews-2023/raw_review_All_Beauty",
        "dataset_url": "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023",
        "source_rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "random_seed": 42,
        "label_strategy": {"1-2": "Negative", "3": "Neutral", "4-5": "Positive"},
        "best_model": best_name,
        "best_f1_macro": float(best_row["f1_macro"]),
        "best_accuracy": float(best_row["accuracy"]),
    }
    with (ROOT / "models" / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(results_df["model"], results_df["f1_macro"], color="#2563eb")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Macro F1-score")
    ax.set_title("Model Comparison")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(ROOT / "reports" / "model_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(results_df.to_string(index=False))
    print(f"\nBest model: {best_name}")


if __name__ == "__main__":
    main()
