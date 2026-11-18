import shutil
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches as PInches, Pt as PPt

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
PRESENTATION = ROOT / "presentation"
REPORTS.mkdir(parents=True, exist_ok=True)
PRESENTATION.mkdir(parents=True, exist_ok=True)

results = pd.read_csv(REPORTS / "model_evaluation_results.csv")
best = results.iloc[0]

# Copy required artifact names to the project root for simple submission access.
for name in ["trained_model.pkl", "tfidf_vectorizer.pkl"]:
    source = ROOT / "models" / name
    if source.exists():
        shutil.copy2(source, ROOT / name)


def add_title(doc, text):
    p = doc.add_paragraph()
    p.style = doc.styles["Title"]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold = True
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(text, style=f"Heading {level}")
    return p


def add_paragraph(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):
        p.add_run(bold_prefix).bold = True
        p.add_run(text[len(bold_prefix):])
    else:
        p.add_run(text)
    return p


def set_IEEE_margins(doc):
    for section in doc.sections:
        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.65)
        section.right_margin = Inches(0.65)


def build_paper():
    doc = Document()
    set_IEEE_margins(doc)
    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(10)

    add_title(doc, "Intelligent Product Review Sentiment Analysis and Customer Feedback Classification Using Natural Language Processing and Machine Learning")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("[Author Name] and [Co-author Name]\n[Department, Institution]  |  [City, State, Country]\n[author.email@example.edu]").italic = True

    add_heading(doc, "Abstract", 1)
    add_paragraph(doc, "This paper presents an end-to-end product-review sentiment analysis system for Positive, Negative, and Neutral classifications. The implementation uses a reproducible subset of the public Amazon Reviews 2023 All_Beauty dataset, with 1–2 star ratings assigned Negative, 3 stars assigned Neutral, and 4–5 stars assigned Positive. Text is cleaned and represented using TF-IDF before model comparison. Logistic Regression, Multinomial Naive Bayes, Linear SVM, and Random Forest are evaluated on a stratified hold-out set. The executed experimental pipeline selected the highest macro-F1 model, which was Logistic Regression (accuracy 0.7282 and macro-F1 0.7294). A lexicon-assisted aspect module identifies quality, price, delivery, packaging, battery life, performance, design, and customer-service opinions. The Streamlit dashboard supports single and bulk analysis, rating mismatch detection, product comparison, aspects, and model transparency.")
    add_paragraph(doc, "Index Terms—Aspect-based sentiment analysis, TF-IDF, logistic regression, natural language processing, product reviews, machine learning.")

    sections = [
        ("I. INTRODUCTION", "Customer reviews provide useful but unstructured evidence about product satisfaction, recurring defects, pricing, delivery, and service. Manual review is costly and inconsistent at large scale. This work develops an interactive machine-learning system that converts review text into sentiment classes while presenting practical aggregate insights."),
        ("II. RELATED WORK", "Pang and Lee [1] established foundational supervised approaches to opinion classification. Pang, Lee, and Vaithyanathan [2] showed that probabilistic text classifiers can classify movie reviews. Liu [3] surveyed sentiment analysis and opinion mining across document, sentence, and aspect levels. Later lexicon and transformer methods improved generalization, but classical TF-IDF pipelines remain reproducible baselines for academic and resource-constrained deployments [4], [5]."),
        ("III. PROBLEM STATEMENT AND OBJECTIVES", "The system accepts a review and predicts Positive, Negative, or Neutral. It should estimate confidence, compare text to a 1–5 rating, support bulk CSV uploads, compare products, extract aspects, and display explainable model metrics. A key limitation is that rating-derived labels are weak labels rather than expert sentiment annotations."),
        ("IV. PROPOSED METHODOLOGY", "The pipeline performs HTML and URL removal, lowercasing, special-character normalization, duplicate removal, TF-IDF feature extraction, train/test splitting, and classifier fitting. Negation words are retained. Stratified 80/20 partitioning occurs before fitting the TF-IDF vectorizer to prevent feature leakage."),
        ("V. SYSTEM ARCHITECTURE", "Reviews pass through data collection, cleaning, TF-IDF extraction, model classification, aspect analysis, dashboard presentation, and downloadable reporting. Fig. 1 summarizes the architecture; Fig. 2 presents the UML use cases."),
        ("VI. DATASET DESCRIPTION AND PREPROCESSING", "Amazon Reviews 2023 was selected because it is a documented public dataset with review text, ratings, item IDs, timestamps, and verification fields [6]. The All_Beauty category is used as a manageable starting subset. The executed processed dataset contains 29,153 deduplicated and cleaned rows. Class sizes are Negative 9,845; Neutral 9,806; and Positive 9,502. Class balance does not imply manual label quality."),
        ("VII. MACHINE LEARNING ALGORITHMS", "Logistic Regression is a discriminative linear classifier. Multinomial Naive Bayes estimates class-conditional word probabilities. Linear SVM seeks a maximum-margin separating boundary. Random Forest combines an ensemble of decision trees. TF-IDF term weights are used with unigram/bigram features."),
        ("VIII. EXPERIMENTAL RESULTS AND DISCUSSION", f"Table I reports actual hold-out results. Logistic Regression obtained the highest macro-F1 value ({best['f1_macro']:.4f}) and accuracy ({best['accuracy']:.4f}). Multinomial Naive Bayes obtained {results.iloc[1]['f1_macro']:.4f} macro-F1, Linear SVM {results.iloc[2]['f1_macro']:.4f}, and Random Forest {results.iloc[3]['f1_macro']:.4f}. The results indicate that a linear TF-IDF baseline is competitive for this weakly labeled review subset. Neutral classification is generally the hardest class. These measurements are not comparable to external benchmarks without identical data and label definitions."),
        ("IX. CONCLUSION AND FUTURE SCOPE", "The study delivered a working sentiment platform with actual model artifacts and empirical metrics. Future work should add expert-labeled or platform-native sentiment annotations, learned aspect models, cross-domain validation, temporal drift monitoring, and calibrated confidence estimates. Emotion labels should use a dedicated emotion dataset before being presented as model predictions rather than lexicon heuristics."),
    ]
    for heading, text in sections:
        add_heading(doc, heading, 1)
        add_paragraph(doc, text)

    add_heading(doc, "TABLE I: ACTUAL MODEL RESULTS", 1)
    table = doc.add_table(rows=1, cols=5)
    table.style = "Table Grid"
    for i, heading in enumerate(["Model", "Accuracy", "Macro Precision", "Macro Recall", "Macro F1"]):
        table.rows[0].cells[i].text = heading
    for _, row in results.iterrows():
        cells = table.add_row().cells
        values = [row["model"], f"{row['accuracy']:.4f}", f"{row['precision_macro']:.4f}", f"{row['recall_macro']:.4f}", f"{row['f1_macro']:.4f}"]
        for i, value in enumerate(values):
            cells[i].text = str(value)

    add_heading(doc, "REFERENCES", 1)
    references = [
        "[1] B. Pang and L. Lee, “Opinion mining and sentiment analysis,” Foundations and Trends in Information Retrieval, vol. 2, no. 1–2, pp. 1–135, 2008.",
        "[2] B. Pang, L. Lee, and S. Vaithyanathan, “Thumbs up? Sentiment classification using machine learning techniques,” in Proc. EMNLP, 2002, pp. 79–86.",
        "[3] B. Liu, Sentiment Analysis and Opinion Mining. Morgan & Claypool, 2012.",
        "[4] C. J. Hutto and E. Gilbert, “VADER: A parsimonious rule-based model for sentiment analysis of social media text,” in Proc. ICWSM, 2014.",
        "[5] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training of deep bidirectional transformers for language understanding,” in Proc. NAACL-HLT, 2019, pp. 4171–4186.",
        "[6] Y. Hou et al., “Bridging language and items for retrieval and recommendation,” arXiv:2403.03952, 2024. Amazon Reviews 2023 documentation: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023.",
    ]
    for ref in references:
        add_paragraph(doc, ref)

    doc.save(REPORTS / "IEEE_Research_Paper.docx")


def build_report():
    doc = Document()
    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(12)

    add_title(doc, "INTELLIGENT PRODUCT REVIEW SENTIMENT ANALYSIS AND CUSTOMER FEEDBACK CLASSIFICATION")
    p = doc.add_paragraph("A Detailed Final-Year B.Tech Project Report")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_paragraph(doc, "Submitted by: [Student Name(s)]")
    add_paragraph(doc, "Department of Computer Science and Engineering / Artificial Intelligence and Machine Learning")
    add_paragraph(doc, "[College Name], [University Name], [Academic Year]")

    add_heading(doc, "CERTIFICATE", 1)
    add_paragraph(doc, "Certified that this project report is submitted as part of the final-year academic requirements. [Project Guide / HOD] verification and institutional signatures should be added before submission.")
    add_heading(doc, "DECLARATION", 1)
    add_paragraph(doc, "We declare that this project work and report describe our implementation and actual experimental outputs. Third-party datasets and academic references are acknowledged. Synthetic or demonstration data is not represented as authentic customer data.")
    add_heading(doc, "ACKNOWLEDGEMENT", 1)
    add_paragraph(doc, "We thank the project guide, department, institution, and the open-data community. We acknowledge the Amazon Reviews 2023 dataset publisher and the cited authors.")

    add_heading(doc, "ABSTRACT", 1)
    add_paragraph(doc, "This project implements an NLP and machine-learning solution for product-review sentiment analysis and customer feedback classification. The system preprocesses real public Amazon review text, derives rating-based weak labels, extracts TF-IDF features, compares four models, displays confusion matrices and metrics, supports bulk CSV processing, detects rating-text mismatches, and exposes aspect-level opinion evidence through Streamlit.")

    chapters = [
        ("Chapter 1: Introduction", "1.1 Background\nE-commerce platforms generate large volumes of review text. Automated classification helps manufacturers and customers summarize opinion trends.\n1.2 Objectives\nThe objectives include three-class sentiment prediction, confidence reporting, rating comparison, bulk processing, product comparison, aspect extraction, and dashboard reporting.\n1.3 Scope and Limitations\nThe first implementation covers the public All_Beauty subset and a lexicon-assisted aspect module. Emotion results are heuristic, and neutral classification remains challenging."),
        ("Chapter 2: Literature Review", "Table and literature discussion cover supervised sentiment classification, opinion mining, lexicons, and transformer methods. Classical TF-IDF baselines remain suitable for explainable resource-efficient deployment."),
        ("Chapter 3: Problem Statement", "Manual analysis is slow and inconsistent. The technical challenge is to classify variable-length text, retain negation, avoid data leakage, compare models fairly, and communicate uncertainty."),
        ("Chapter 4: Proposed Methodology", "Data collection → cleaning → deduplication → rating label derivation → stratified split → TF-IDF fitting → model training → test evaluation → aspect analysis → dashboard presentation."),
        ("Chapter 5: System Design", "The architecture and UML use cases are documented in docs/system_architecture.md. Data artifacts, model files, source modules, application, reports, and presentation assets are separated by responsibility."),
        ("Chapter 6: Implementation", "The Python implementation uses pandas, scikit-learn, Streamlit, matplotlib, Plotly, python-docx, and python-pptx. TF-IDF is fitted only on training data. The system stores the best model and vectorizer as pickle artifacts."),
        ("Chapter 7: Results and Discussion", f"The executed hold-out test used 29,153 processed rows. Logistic Regression achieved accuracy {best['accuracy']:.4f} and macro-F1 {best['f1_macro']:.4f}. A complete model comparison is available in reports/model_evaluation_results.csv and in model_comparison.png. Accuracy alone is not used to select the best model because macro-F1 protects minority and neutral class performance."),
        ("Chapter 8: Conclusion and Future Scope", "The project demonstrates a complete sentiment-analysis pipeline and dashboard. Future work includes an expert-labeled dataset, cross-platform validation, learned aspect extraction, DistilBERT comparison, calibrated probabilities, authentication, database storage, and deployment."),
    ]
    for heading, text in chapters:
        add_heading(doc, heading, 1)
        for block in text.split("\n"):
            add_paragraph(doc, block)

    add_heading(doc, "REFERENCES", 1)
    for ref in [
        "Pang, B., and Lee, L., “Opinion Mining and Sentiment Analysis,” Foundations and Trends in Information Retrieval, 2008.",
        "Liu, B., Sentiment Analysis and Opinion Mining, Morgan & Claypool, 2012.",
        "Hutto, C.J., and Gilbert, E., “VADER,” ICWSM, 2014.",
        "Devlin, J. et al., “BERT: Pre-training of Deep Bidirectional Transformers,” NAACL-HLT, 2019.",
        "Hou, Y. et al., “Bridging Language and Items for Retrieval and Recommendation,” arXiv:2403.03952, 2024.",
        "McAuley-Lab, Amazon Reviews 2023 dataset documentation, Hugging Face, https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023.",
    ]:
        add_paragraph(doc, ref)

    add_heading(doc, "APPENDIX", 1)
    add_paragraph(doc, "A. Execution command: .\\.venv310\\Scripts\\python.exe src\\train_models.py")
    add_paragraph(doc, "B. Dashboard command: .\\.venv310\\Scripts\\python.exe -m streamlit run app\\app.py")
    add_paragraph(doc, "C. Label strategy: 1–2 = Negative, 3 = Neutral, 4–5 = Positive.")
    add_paragraph(doc, "D. Integrity note: all source metrics come from the executed hold-out evaluation. Confusion matrix figures are generated from test predictions.")

    doc.save(REPORTS / "Project_Report.docx")


def build_presentation():
    prs = Presentation()
    prs.slide_width = PInches(13.333)
    prs.slide_height = PInches(7.5)

    blue = RGBColor(37, 99, 235)
    navy = RGBColor(15, 23, 42)
    gray = RGBColor(71, 85, 105)

    slides = [
        ("Intelligent Product Review Sentiment Analysis", "Customer Feedback Classification using NLP and ML", None),
        ("Abstract", "End-to-end sentiment system using TF-IDF and four classical ML classifiers. Actual best model: Logistic Regression (macro-F1 0.7294).", None),
        ("Introduction", "High-volume review text is unstructured, inconsistent, and difficult to analyze manually.", None),
        ("Problem Statement", "Classify review opinion and support rating comparisons, bulk analysis, product comparison, and aspect extraction.", None),
        ("Motivation", "Turn opinions into operational insight: satisfaction, complaints, trust, and improvement opportunities.", None),
        ("Project Objectives", "• Three sentiment classes  • Confidence  • Rating mismatch  • Bulk CSV  • Product and aspect analytics", None),
        ("Existing System", "Manual review reading or simple star aggregation without semantic context.", None),
        ("Limitations of Existing System", "Subjective, slow, cannot process scale, misses mixed opinions and aspect evidence.", None),
        ("Proposed System", "Streamlit application with TF-IDF models, rule-assisted aspects, and downloadable outputs.", None),
        ("Literature Review", "Foundational supervised opinion mining [1][2]; aspect-aware opinion mining [3]; lexicons [4]; transformers [5].", None),
        ("System Architecture", "Dataset → Cleaning → TF-IDF → Models → Classification → Aspects → Dashboard → Insights", None),
        ("Dataset Description", "Amazon Reviews 2023 All_Beauty; 29,153 processed rows; 1–2 Negative, 3 Neutral, 4–5 Positive.", None),
        ("Data Preprocessing", "HTML/URL removal, lowercasing, duplicate removal, text normalization, and negation retention; split before TF-IDF.", None),
        ("Machine Learning Algorithms", "Logistic Regression • Multinomial Naive Bayes • Linear SVM • Random Forest", None),
        ("Aspect-Based Sentiment Analysis", "Quality • Price • Delivery • Packaging • Battery • Performance • Design • Customer service", None),
        ("Dashboard Implementation", "Seven-page Streamlit interface for single/bulk analysis, analytics, comparisons, aspects, and metrics.", None),
        ("Experimental Results", "Actual hold-out accuracy: Logistic Regression 0.7282; macro-F1 0.7294.", str(ROOT / "reports" / "model_comparison.png")),
        ("Model Performance Comparison", f"Best model: {best['model']}. Macro-F1: {best['f1_macro']:.4f}. Neutral is the lowest-performing class overall.", str(ROOT / "reports" / "model_comparison.png")),
        ("Conclusion", "The project demonstrates an end-to-end, reproducible system. Rating-derived labels and the lexicon ABSA module are documented limitations.", None),
        ("Future Scope and References", "Learned ABSA • DistilBERT • expert labels • drift monitoring • deployment • [1]–[6]", None),
    ]

    for index, (title, body, image) in enumerate(slides):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(248, 250, 252)

        accent = slide.shapes.add_shape(1, 0, 0, PInches(0.18), prs.slide_height)
        accent.fill.solid()
        accent.fill.fore_color.rgb = blue
        accent.line.fill.background()

        title_box = slide.shapes.add_textbox(PInches(0.65), PInches(0.45), PInches(12), PInches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = PPt(28)
        p.font.bold = True
        p.font.color.rgb = navy

        body_box = slide.shapes.add_textbox(PInches(0.75), PInches(1.45), PInches(11.8), PInches(4.8))
        tf = body_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = body
        p.font.size = PPt(19)
        p.font.color.rgb = gray

        if image and Path(image).exists():
            body_box.left = PInches(6.8)
            body_box.width = PInches(5.8)
            slide.shapes.add_picture(image, PInches(0.65), PInches(2.0), width=PInches(5.8), height=PInches(3.8))

        footer = slide.shapes.add_textbox(PInches(11.8), PInches(7.05), PInches(0.8), PInches(0.25))
        fp = footer.text_frame.paragraphs[0]
        fp.text = f"{index + 1:02d}"
        fp.font.size = PPt(9)
        fp.font.color.rgb = gray
        fp.alignment = PP_ALIGN.RIGHT

        notes = slide.notes_slide.notes_text_frame
        notes.text = f"Speaker notes: Present {title.lower()} clearly and explain that actual experimental values are taken from the executed hold-out pipeline. Avoid overstating weakly supervised results."

    prs.save(PRESENTATION / "Product_Review_Presentation.pptx")


if __name__ == "__main__":
    build_paper()
    build_report()
    build_presentation()
    print("Generated IEEE paper DOCX, project report DOCX, and 20-slide presentation PPTX.")
