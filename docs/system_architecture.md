# System Architecture

```mermaid
flowchart TD
    A[Customer Reviews Dataset] --> B[Data Collection]
    B --> C[Cleaning and Preprocessing]
    C --> D[TF-IDF Feature Extraction]
    D --> E[Train/Test Split]
    E --> F1[Logistic Regression]
    E --> F2[Multinomial Naive Bayes]
    E --> F3[Linear SVM]
    E --> F4[Random Forest]
    F1 --> G[Sentiment Classification]
    F2 --> G
    F3 --> G
    F4 --> G
    G --> H[Aspect Lexicon and Phrase Analysis]
    G --> I[Rating-Sentiment Mismatch Analysis]
    H --> J[Streamlit Analytics Dashboard]
    I --> J
    J --> K[Business Insights and Reports]
```

## UML Use Case

```mermaid
flowchart LR
    U[User / Analyst]
    U --> UC1[Enter a review]
    U --> UC2[Upload CSV]
    U --> UC3[View sentiment confidence]
    U --> UC4[Compare products]
    U --> UC5[Explore aspect opinions]
    U --> UC6[Download analyzed CSV]
    U --> UC7[View model performance]

    UC2 --> S[Streamlit Application]
    UC1 --> S
    UC3 --> S
    UC4 --> S
    UC5 --> S
    UC6 --> S
    UC7 --> S

    S --> M[Sentiment Model and TF-IDF Pipeline]
    S --> A[Aspect Analyzer]
    S --> DB[(Optional SQLite Database)]
```

## Component Responsibilities

- `src/preprocessing.py`: cleaning, deduplication, split-safe text preparation.
- `src/train_models.py`: model training and evaluation.
- `src/aspect_analysis.py`: aspect lexicons and opinion extraction.
- `src/predict.py`: loading artifacts and producing predictions.
- `app/app.py`: interactive dashboard.
- `data/`: raw and processed datasets.
- `models/`: trained artifacts and evaluation outputs.
- `reports/`: figures and academic report source outputs.
- `presentation/`: PowerPoint source and assets.
