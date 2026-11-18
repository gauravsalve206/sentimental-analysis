from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
import shutil

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
results = pd.read_csv(REPORTS / "model_evaluation_results.csv")
best = results.iloc[0]


def build_pdf(path, title, subtitle, sections):
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=45, leftMargin=45,
                            topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CenterTitle", parent=styles["Title"], alignment=TA_CENTER,
                              textColor=colors.HexColor("#0f172a")))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], textColor=colors.HexColor("#1d4ed8")))
    story = [Paragraph(title, styles["CenterTitle"]), Spacer(1, 12),
             Paragraph(subtitle, styles["Normal"]), Spacer(1, 18)]
    for heading, text in sections:
        story += [Paragraph(heading, styles["Section"]), Paragraph(text, styles["Normal"]), Spacer(1, 10)]
    doc.build(story)


paper_sections = [
    ("Abstract", f"This project implements an end-to-end product-review sentiment system using TF-IDF and four classical classifiers. The actual hold-out evaluation selected Logistic Regression as the best model, with accuracy {best['accuracy']:.4f} and macro-F1 {best['f1_macro']:.4f}."),
    ("I. Introduction", "Customer review text provides scalable evidence of satisfaction and complaints. The system classifies Positive, Negative, and Neutral sentiment and supports dashboard-level analytics."),
    ("II. Dataset and Labeling", "The public Amazon Reviews 2023 All_Beauty subset was used. A weak strategy maps ratings 1–2 to Negative, 3 to Neutral, and 4–5 to Positive. These labels are not expert sentiment annotations."),
    ("III. Methodology", "Text is cleaned, deduplicated, split into stratified train/test partitions, and transformed with TF-IDF. The vectorizer is fitted only on training text."),
    ("IV. Algorithms", "The compared models are Logistic Regression, Multinomial Naive Bayes, Linear SVM, and Random Forest."),
    ("V. Results", f"The executed hold-out dataset contained 29,153 processed rows. The best measured model was {best['model']} with accuracy {best['accuracy']:.4f}, macro precision {best['precision_macro']:.4f}, macro recall {best['recall_macro']:.4f}, and macro F1 {best['f1_macro']:.4f}."),
    ("VI. Conclusion", "The completed implementation includes preprocessing, model evaluation, aspect assistance, and a Streamlit dashboard. Future work should use expert labels and learned aspect extraction."),
]

report_sections = [
    ("Abstract", "This report documents the dataset, preprocessing, model training, results, design, implementation, limitations, and future scope of the product-review sentiment system."),
    ("Chapter 1: Introduction", "The project addresses the manual cost and inconsistency of understanding large volumes of customer feedback."),
    ("Chapter 2: Methodology", "The pipeline includes cleaning, duplicate removal, weak rating-label derivation, split-before-transform, TF-IDF, model comparison, and Streamlit presentation."),
    ("Chapter 3: System Design", "Source modules separate preprocessing, prediction, aspect analysis, training, and dashboard responsibilities."),
    ("Chapter 4: Implementation", "The system uses pandas, NumPy, scikit-learn, NLTK/TextBlob utilities, Streamlit, Plotly, and document-generation libraries."),
    ("Chapter 5: Results", f"Actual macro-F1 for Logistic Regression was {best['f1_macro']:.4f}; accuracy was {best['accuracy']:.4f}. Complete metrics are in reports/model_evaluation_results.csv."),
    ("Chapter 6: Conclusion and Future Scope", "The project is complete for a classical baseline implementation. Future work should include expert annotations, cross-domain testing, transformer comparison, drift monitoring, database storage, and deployment."),
]

build_pdf(REPORTS / "IEEE_Research_Paper.pdf",
          "Intelligent Product Review Sentiment Analysis and Customer Feedback Classification",
          "IEEE-Format Academic Summary | [Author placeholders]",
          paper_sections)

build_pdf(REPORTS / "Project_Report.pdf",
          "Intelligent Product Review Sentiment Analysis and Customer Feedback Classification",
          "Detailed B.Tech Project Report",
          report_sections)
print("Generated PDF reports.")

# Copy final PDFs to the submission root alongside the requested artifacts.
for name in ["IEEE_Research_Paper.pdf", "Project_Report.pdf"]:
    shutil.copy2(REPORTS / name, ROOT / name)
