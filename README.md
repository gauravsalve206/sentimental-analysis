# Intelligent Product Review Sentiment Analysis

This repository is being developed as a complete academic final-year project for sentiment classification and product-review analytics.

## Project Status

Initial stage completed:

- Workspace structure created.
- Dataset selection and integrity plan documented.
- System architecture and UML use-case descriptions created.

Implementation stages remain: dataset acquisition, preprocessing, model training, dashboard, report, paper, and presentation generation.

## Dataset

The primary selected source is **Amazon Reviews 2023 (McAuley-Lab)**. The initial category is All Beauty. The source is publicly documented at:

https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023

Rating 1–2 is treated as Negative, rating 3 as Neutral, and rating 4–5 as Positive. This is explicitly a rating-derived weak label rather than a manually verified sentiment label.

## Documentation

- `docs/research_plan.md`
- `docs/system_architecture.md`

## Planned Structure

- `app/` — Streamlit application
- `data/raw/` — downloaded source data
- `data/processed/` — cleaned, reproducible datasets
- `src/` — preprocessing, training, prediction, and aspect modules
- `models/` — trained models and evaluation artifacts
- `notebooks/` — reproducible Jupyter notebook
- `presentation/` — PowerPoint assets and source
- `reports/` — research paper and project report assets
- `tests/` — unit tests

## Run the Dashboard

```powershell
.\.venv310\Scripts\python.exe -m streamlit run app\app.py
```

## Train or Reproduce Models

```powershell
.\.venv310\Scripts\python.exe src\train_models.py
```

## Actual Executed Results

The four-model hold-out evaluation is stored in `reports/model_evaluation_results.csv` and the project-root copy `model_evaluation_results.csv`. Logistic Regression was selected because it achieved the highest macro-F1 score:

- Accuracy: 0.728177
- Macro precision: 0.729678
- Macro recall: 0.729134
- Macro F1: 0.729387

Sentiment labels are weak ratings-derived labels: 1–2 Negative, 3 Neutral, 4–5 Positive. They are not expert-verified sentiment annotations.

## Downloadable Deliverables

- `Product_Review_Sentiment_Analysis.ipynb`
- `IEEE_Research_Paper.docx` and `IEEE_Research_Paper.pdf`
- `Product_Review_Presentation.pptx`
- `Project_Report.docx` and `Project_Report.pdf`
- `app/app.py`
- `requirements.txt`
- `trained_model.pkl`
- `tfidf_vectorizer.pkl`
- `sample_reviews.csv`
- `model_evaluation_results.csv`

The emotion labels and aspect analyzer are heuristics, not separately trained models. This distinction is retained throughout the dashboard and academic deliverables.
