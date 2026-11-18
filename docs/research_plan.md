# Research Plan and Dataset Selection

## 1. Project Scope

The system classifies product-review text as Positive, Negative, or Neutral and analyzes 1–5 star ratings, mismatches, products, aspects, and aggregate customer satisfaction. Emotion labels are an optional advanced extension; no emotion classifier will be reported as trained unless a valid emotion-labeled dataset is available.

## 2. Selected Dataset

**Primary source:** Amazon Reviews 2023 (McAuley-Lab), accessible from Hugging Face.

- Category used initially: `raw_review_All_Beauty` (manageable subset; scalable to additional categories).
- Source: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- Review fields: `rating`, `title`, `text`, `asin`, `parent_asin`, `timestamp`, `verified_purchase`, `helpful_vote`.
- Review counts and metadata are supplied by the dataset publisher and should be recorded from the actual downloaded subset.

### Labeling Strategy

No manually verified sentiment field is assumed in the source. The documented weak-supervision strategy is:

| Rating | Sentiment label |
|---|---|
| 1–2 | Negative |
| 3 | Neutral |
| 4–5 | Positive |

The labels are derived from numerical ratings and are therefore only proxy sentiment labels, not ground truth for the independent meaning of review text.

### Limitations

- Rating-based labels can disagree with wording.
- Neutral reviews are frequently sparse or ambiguous.
- The chosen category may not represent every Amazon category or Flipkart customers.
- URLs, HTML, marketing text, and duplicate reviews require cleaning.
- The dataset is not a complete representation of all e-commerce platforms.
- Public availability and data terms must be verified before redistribution. Raw review data is stored locally only for project use.

## 3. Execution Stages

1. Download or cache a category-specific public dataset.
2. Validate fields and remove rows with missing/duplicate review text.
3. Preprocess text while preserving negation terms.
4. Stratify an 80/20 split before TF-IDF fitting.
5. Train Logistic Regression, Multinomial Naive Bayes, Linear SVM, and Random Forest.
6. Report accuracy, macro precision, macro recall, macro F1, confusion matrices, and one-vs-rest AUC if the split contains all classes.
7. Select the model strictly from measured test performance.
8. Add lexicon/rule-assisted aspect extraction and clearly label it as interpretable rather than a learned ABSA model.
9. Build the Streamlit interface and export all models, figures, tables, and documentation.

## 4. Reproducibility Controls

- Fixed random seed.
- Split before vectorizer/model fitting.
- No duplicate text across train/test partitions.
- Save preprocessing and model pipeline or separate fitted artifacts.
- Record package versions and exact downloaded sample size.
- Generate evaluation results only after executing the pipeline.

## 5. Ethical and Academic Integrity

This project does not claim that synthetic text is authentic customer data. It distinguishes source datasets, demonstration entries, and user-entered content throughout the app and documents.
