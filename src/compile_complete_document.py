from pathlib import Path
import json
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)
OUT = REPORTS / "Complete_Project_Report_and_IEEE_Paper.docx"
ROOT_OUT = ROOT / "Complete_Project_Report_and_IEEE_Paper.docx"

results = pd.read_csv(REPORTS / "model_evaluation_results.csv")
processed = pd.read_csv(ROOT / "data" / "processed" / "processed_reviews.csv")
metadata = json.loads((ROOT / "models" / "metadata.json").read_text(encoding="utf-8"))
best = results.iloc[0]


def set_cell_text(cell, text, bold=False):
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(str(text))
    r.bold = bold
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


def set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def add_heading(doc, text, level=1):
    return doc.add_heading(text, level=level)


def add_para(doc, text="", bold=False, italic=False, align=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    return p


def add_bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def set_margins(section, left=0.75, right=0.75, top=0.7, bottom=0.7):
    section.left_margin = Inches(left)
    section.right_margin = Inches(right)
    section.top_margin = Inches(top)
    section.bottom_margin = Inches(bottom)


def add_page_number(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def add_figure(doc, path, caption, width=6.2):
    if Path(path).exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path), width=Inches(width))
        c = doc.add_paragraph()
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.add_run(caption)
        r.italic = True
        r.font.size = Pt(9)


doc = Document()
section = doc.sections[0]
set_margins(section)
add_page_number(section)

styles = doc.styles
styles["Normal"].font.name = "Times New Roman"
styles["Normal"].font.size = Pt(11)
styles["Title"].font.name = "Times New Roman"
styles["Title"].font.size = Pt(24)
for level in range(1, 4):
    styles[f"Heading {level}"].font.name = "Arial"
    styles[f"Heading {level}"].font.color.rgb = RGBColor(31, 78, 121)

# COVER AND FRONT MATTER
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(55)
r = p.add_run("INTELLIGENT PRODUCT REVIEW SENTIMENT ANALYSIS AND CUSTOMER FEEDBACK CLASSIFICATION")
r.bold = True
r.font.size = Pt(24)
r.font.name = "Times New Roman"
add_para(doc, "USING NATURAL LANGUAGE PROCESSING AND MACHINE LEARNING", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
add_para(doc, "A Complete Final-Year B.Tech Project Report and IEEE Conference-Format Research Paper", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
add_para(doc, "\nSubmitted by: [Student Name / Roll Number]\nDepartment of Computer Science and Engineering / Artificial Intelligence and Machine Learning\n[College Name]  |  [University Name]  |  [Academic Year]", align=WD_ALIGN_PARAGRAPH.CENTER)
add_para(doc, "\nProject Guide: [Name and Designation]", align=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_page_break()

add_heading(doc, "Certificate", 1)
add_para(doc, "This is to certify that the project entitled “Intelligent Product Review Sentiment Analysis and Customer Feedback Classification Using Natural Language Processing and Machine Learning” was completed and documented for academic submission. The project guide, Head of Department, and authorized institutional representatives must add the final signatures and institutional seal before submission.")
add_para(doc, "Project Guide: ____________________    Date: ____________________")
add_para(doc, "Head of Department: ______________    External Examiner: __________")
add_heading(doc, "Declaration", 1)
add_para(doc, "We declare that this project report and associated implementation describe our work and use publicly accessible or documented third-party resources only where acknowledged. No presented accuracy, chart, or result is invented. Rating-derived sentiment labels are explicitly distinguished from expert sentiment annotations. Synthetic examples are not represented as real customer reviews.")
add_heading(doc, "Acknowledgement", 1)
add_para(doc, "We acknowledge the project guide, department faculty, institution, open-source developer community, and dataset publishers. We also acknowledge the authors of the academic literature cited in this document.")
add_heading(doc, "Abstract", 1)
add_para(doc, "This project presents an end-to-end system for automatically classifying product-review text as Positive, Negative, or Neutral. It integrates document cleaning, duplicate removal, weak rating-derived labeling, TF-IDF feature extraction, train-test separation, four machine-learning baselines, aspect evidence extraction, mismatch analysis, bulk processing, and a Streamlit dashboard. The public Amazon Reviews 2023 All_Beauty dataset was used for a manageable 29,153-row processed subset. After fitting preprocessing only on training data, the models achieved test results summarized in Table 1. Logistic Regression was selected as the best model because it obtained the highest macro-F1 score: 0.729387. It also achieved 0.728177 accuracy. The work is explicitly limited by weak ratings-derived labels, lack of expert aspect annotations, and rule-assisted emotion/aspect outputs.")
add_para(doc, "Index Terms: Sentiment analysis, natural language processing, product reviews, TF-IDF, logistic regression, naive Bayes, support vector machine, random forest, aspect analysis.")

doc.add_page_break()
add_heading(doc, "Table of Contents", 1)
add_para(doc, "For the Word file, update the field manually in Microsoft Word: References → Table of Contents → Automatic Table.")
toc = doc.add_paragraph()
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
toc._p.append(fld)

add_heading(doc, "List of Major Figures and Tables", 1)
add_bullets(doc, [
    "Figure 1: System architecture.",
    "Figure 2: UML use-case workflow.",
    "Figure 3: Model comparison chart.",
    "Figure 4: Example confusion matrix.",
    "Table 1: Experimental model metrics.",
    "Table 2: Dataset field and label summary.",
    "Table 3: Preprocessing operations.",
    "Table 4: Algorithm comparison.",
])

doc.add_page_break()
add_heading(doc, "PART A: COMPLETE PROJECT REPORT", 1)

add_heading(doc, "Chapter 1: Introduction", 1)
add_heading(doc, "1.1 Project Background", 2)
add_para(doc, "E-commerce platforms generate extensive customer opinions, but raw review text is too large and unstructured for purely manual analysis. The project converts such text into three broad sentiment classes and combines it with numerical ratings and product metadata. It is designed for students, merchants, and analysts who need understandable explanations rather than only a binary score.")
add_heading(doc, "1.2 Motivation", 2)
add_para(doc, "Automatic sentiment analysis can reduce review-reading workload, identify repeated defects, measure satisfaction trends, compare products, and highlight potentially urgent customer complaints. It does not replace human judgment for policy-sensitive decisions.")
add_heading(doc, "1.3 Objectives", 2)
add_bullets(doc, [
    "Analyze manually entered and uploaded review text.",
    "Classify each review as Positive, Negative, or Neutral and provide confidence.",
    "Compare written sentiment with 1–5 star ratings.",
    "Support bulk CSV analysis and downloadable results.",
    "Compare products using review distributions and average ratings.",
    "Identify positive and negative evidence for configured product aspects.",
    "Compare four machine-learning baselines using a transparent hold-out test.",
    "Provide a responsive Streamlit dashboard and reproducible academic artifacts.",
])
add_heading(doc, "1.4 Scope and Deliverables", 2)
add_para(doc, "The implemented scope is a TF-IDF and classical-machine-learning baseline for the All_Beauty category. DistilBERT and deep learning are identified as optional future extensions rather than trained claims. Emotion labels and aspect sentiment are heuristic capabilities, not separately trained classifiers.")
add_heading(doc, "1.5 Limitations", 2)
add_bullets(doc, [
    "Numerical ratings are imperfect proxies for text sentiment.",
    "The selected category may not generalize to every product or platform.",
    "Neutral examples are semantically varied and difficult to learn.",
    "Lexicon-based aspect extraction can miss implicit opinions.",
    "Emotion detection is heuristic and should not be presented as emotion-model accuracy.",
])

add_heading(doc, "Chapter 2: Literature Review", 1)
add_para(doc, "Pang and Lee [1] reviewed sentiment and opinion analysis as a major natural-language-processing problem. Pang, Lee, and Vaithyanathan [2] demonstrated supervised sentiment classification on user-generated text using bag-of-words representations. Liu [3] formalized document, sentence, and aspect-level opinion analysis, emphasizing that an overall sentiment score may hide positive and negative opinions about different attributes. Sebastiani [4] described supervised text categorization foundations relevant to term weighting and classifier selection.")
add_para(doc, "Joachims [5] demonstrated support-vector methods for text classification, while Hutto and Gilbert [6] introduced VADER as a practical rule-based social-media sentiment system. Devlin et al. [7] established bidirectional transformer pre-training that later enabled strong transfer learning through models such as BERT and DistilBERT. The present project uses TF-IDF plus interpretable linear and ensemble baselines, making it suitable for a controlled academic implementation and reproducible comparison.")

add_heading(doc, "Chapter 3: Dataset and Labeling", 1)
add_heading(doc, "3.1 Source Selection", 2)
add_para(doc, "The primary source is Amazon Reviews 2023 by McAuley-Lab, a large public dataset distributed for retrieval and recommendation research [8]. The initial All_Beauty raw review subset contains 701,528 rows in the downloaded source and is far too large for initial model experiments. The project created a balanced and manageable sample, then cleaned and deduplicated it for a final processed dataset of 29,153 rows.")

review_counts = processed["sentiment"].value_counts().to_dict()
t = doc.add_table(rows=1, cols=3)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(["Field", "Project Usage", "Availability"]):
    set_cell_text(t.rows[0].cells[i], h, True)
    set_cell_shading(t.rows[0].cells[i], "D9EAF7")
set_repeat_table_header(t.rows[0])
for row in [
    ("rating", "Weak label and rating analytics", "Downloaded"),
    ("text", "Preprocessing and TF-IDF features", "Downloaded"),
    ("title", "Available, but final text model used body text", "Downloaded"),
    ("asin / parent_asin", "Product and comparison grouping", "Downloaded"),
    ("timestamp", "Optional temporal analysis", "Downloaded"),
    ("verified_purchase", "Optional integrity attribute", "Downloaded"),
    ("helpful_vote", "Available but not a model feature", "Downloaded"),
]:
    cells = t.add_row().cells
    for i, value in enumerate(row): set_cell_text(cells[i], value)
add_para(doc, f"Processed class distribution: Negative={review_counts.get('Negative',0):,}; Neutral={review_counts.get('Neutral',0):,}; Positive={review_counts.get('Positive',0):,}.", italic=True)

add_heading(doc, "3.2 Weak Labeling Strategy", 2)
t = doc.add_table(rows=1, cols=2)
t.style = "Table Grid"
for i, h in enumerate(["Rating", "Derived Sentiment"]):
    set_cell_text(t.rows[0].cells[i], h, True)
    set_cell_shading(t.rows[0].cells[i], "D9EAF7")
for row in [("1–2", "Negative"), ("3", "Neutral"), ("4–5", "Positive")]:
    cells = t.add_row().cells
    set_cell_text(cells[0], row[0]); set_cell_text(cells[1], row[1])

add_heading(doc, "Chapter 4: Data Preprocessing and Feature Engineering", 1)
t = doc.add_table(rows=1, cols=3)
t.style = "Table Grid"
for i, h in enumerate(["Operation", "Implementation", "Reason"]):
    set_cell_text(t.rows[0].cells[i], h, True)
    set_cell_shading(t.rows[0].cells[i], "D9EAF7")
set_repeat_table_header(t.rows[0])
for row in [
    ("Missing text", "Remove empty rows", "Prevents invalid model input"),
    ("Duplicate removal", "Deduplicate normalized text", "Prevents repeated examples"),
    ("Lowercasing", "Convert text to lower case", "Normalizes vocabulary"),
    ("HTML removal", "Strip HTML tags", "Removes markup"),
    ("URL removal", "Replace web addresses", "Removes noise"),
    ("Special characters", "Preserve words, punctuation and negation-sensitive characters", "Retains useful sentiment text"),
    ("Whitespace", "Collapse repeated spaces", "Creates consistent tokens"),
    ("Leaking protection", "Stratified split precedes TF-IDF fitting", "Ensures no test features inform training"),
]:
    cells = t.add_row().cells
    for i, value in enumerate(row): set_cell_text(cells[i], value)

add_heading(doc, "4.1 Feature Extraction", 2)
add_para(doc, "The TF-IDF vectorizer uses unigram and bigram features, sublinear term frequency scaling, a minimum document frequency of 2, and a 50,000-feature limit. The 80/20 split is stratified, and the random seed is 42. Training rows = 23,322 and test rows = 5,831.")

add_heading(doc, "Chapter 5: System Architecture and Design", 1)
add_para(doc, "The architecture follows a staged pipeline: source review collection, cleaning and deduplication, weak labeling, train/test partition, TF-IDF transformation, model comparison, test evaluation, aspect analysis, rating mismatch detection, analytics, and report generation.")
add_figure(doc, ROOT / "reports" / "model_comparison.png", "Figure 1: Executed model comparison visualization.", 6.0)

add_heading(doc, "5.1 UML Use Cases", 2)
add_bullets(doc, [
    "Enter a product review and receive sentiment, confidence, and heuristic emotion.",
    "Upload a CSV and download batch predictions.",
    "Inspect product-level sentiment, rating, and mismatch information.",
    "Select multiple products and compare distributions.",
    "Extract aspect evidence and identify improvement areas.",
    "View model accuracy and confusion matrices.",
])

add_heading(doc, "Chapter 6: Machine-Learning Implementation", 1)
add_heading(doc, "6.1 Algorithms", 2)
t = doc.add_table(rows=1, cols=3)
t.style = "Table Grid"
for i, h in enumerate(["Algorithm", "Representation", "Role"]):
    set_cell_text(t.rows[0].cells[i], h, True); set_cell_shading(t.rows[0].cells[i], "D9EAF7")
for row in [
    ("Logistic Regression", "TF-IDF", "Discriminative linear baseline"),
    ("Multinomial Naive Bayes", "TF-IDF", "Probabilistic word-frequency baseline"),
    ("Linear SVM", "TF-IDF", "Maximum-margin linear classifier"),
    ("Random Forest", "TF-IDF", "Bagged decision-tree ensemble"),
]:
    cells = t.add_row().cells
    for i, value in enumerate(row): set_cell_text(cells[i], value)

add_heading(doc, "6.2 Evaluation Method", 2)
add_para(doc, "The system reports accuracy, macro precision, macro recall, macro F1, per-class precision/recall/F1, confusion matrices, and ROC-AUC where the classifier provides a suitable probability or score interface. Macro averages give every class equal weight, making the neutral class more visible than accuracy alone.")

add_heading(doc, "Chapter 7: Experimental Results and Discussion", 1)
t = doc.add_table(rows=1, cols=5)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(["Model", "Accuracy", "Macro Precision", "Macro Recall", "Macro F1"]):
    set_cell_text(t.rows[0].cells[i], h, True); set_cell_shading(t.rows[0].cells[i], "D9EAF7")
set_repeat_table_header(t.rows[0])
for _, row in results.iterrows():
    cells = t.add_row().cells
    values = [row["model"], f"{row['accuracy']:.4f}", f"{row['precision_macro']:.4f}", f"{row['recall_macro']:.4f}", f"{row['f1_macro']:.4f}"]
    for i, value in enumerate(values): set_cell_text(cells[i], value)

add_para(doc, f"The selected model is {best['model']}. Its test accuracy is {best['accuracy']:.4f}, macro precision is {best['precision_macro']:.4f}, macro recall is {best['recall_macro']:.4f}, and macro F1 is {best['f1_macro']:.4f}.", bold=True)
add_para(doc, "The result should not be generalized to another platform or expert-labeled dataset without a repeated validation process. The neutral class is the least consistently separated class in this weakly labeled experimental setup.")

for model_name in results["model"]:
    slug = model_name.lower().replace(" ", "_")
    cm = REPORTS / f"confusion_{slug}.png"
    if cm.exists():
        add_figure(doc, cm, f"Figure: Confusion matrix for {model_name}.", 5.4)

add_heading(doc, "Chapter 8: Dashboard and Application Modules", 1)
add_bullets(doc, [
    "Home: objectives, dataset overview, and project features.",
    "Single Review: text entry, predicted sentiment, confidence, heuristic emotion, and rating mismatch.",
    "Bulk Analysis: CSV upload, row-level results, download, and distribution chart.",
    "Product Analytics: review count, sentiment percentages, average rating, and visual distributions.",
    "Product Comparison: multi-product selection and ratings/sentiment comparison.",
    "Aspect Analysis: positive/negative evidence for quality, price, delivery, packaging, battery, performance, design, and service.",
    "Model Performance: model table and generated confusion matrices.",
])

add_heading(doc, "Chapter 9: Aspect-Based Sentiment and Automated Insights", 1)
add_para(doc, "Aspect analysis is lexicon-assisted. It identifies sentence fragments associated with configured terms, then counts positive and negative opinion words. If positive evidence dominates, the aspect is Positive; if negative evidence dominates, it is Negative; otherwise it is Neutral. This implementation is explainable but does not perform learned target-opinion extraction.")

add_heading(doc, "Chapter 10: Testing and Deployment", 1)
add_para(doc, "Python source was compiled successfully. Direct assertions validated negation preservation, rating labeling, and aspect extraction. The Streamlit application was started on port 8501 for smoke testing. The virtual environment uses Python 3.10 for package compatibility. The dashboard can be launched with: .\\.venv310\\Scripts\\python.exe -m streamlit run app\\app.py")

add_heading(doc, "Chapter 11: Conclusion and Future Scope", 1)
add_para(doc, "The project successfully implements a complete classical NLP sentiment-analysis pipeline and interactive analytics dashboard. It uses documented public data, prevents feature leakage, compares four algorithms, preserves explicit academic limitations, and exports reproducible artifacts. Future work should collect expert annotations, evaluate cross-platform reviews, implement learned aspect extraction, compare DistilBERT or BERT, calibrate confidence scores, monitor drift, add persistent database storage, and deploy the service securely.")

add_heading(doc, "Project Appendix", 1)
add_heading(doc, "A. Source Structure", 2)
add_bullets(doc, [
    "app/app.py — Streamlit dashboard",
    "src/preprocessing.py — cleaning and label logic",
    "src/train_models.py — training and evaluation",
    "src/predict.py — artifact loading and prediction",
    "src/aspect_analysis.py — lexicon-assisted aspect extraction",
    "models/ — trained model and TF-IDF vectorizer",
    "data/ — raw and processed datasets",
    "reports/ — metrics and visualizations",
])
add_heading(doc, "B. Reproduction Commands", 2)
add_para(doc, "Train: .\\.venv310\\Scripts\\python.exe src\\train_models.py")
add_para(doc, "Run dashboard: .\\.venv310\\Scripts\\python.exe -m streamlit run app\\app.py")
add_heading(doc, "C. Integrity and Ethics", 2)
add_para(doc, "The dashboard distinguishes user-entered text, actual public-source reviews, and demonstration examples. It does not claim weak rating labels are human sentiment labels or that heuristic emotion/aspect outputs are trained emotion/aspect models.")

# IEEE PAPER PART
new_section = doc.add_section(WD_SECTION.NEW_PAGE)
set_margins(new_section, left=0.55, right=0.55, top=0.55, bottom=0.55)
add_page_number(new_section)

add_heading(doc, "PART B: IEEE CONFERENCE-FORMAT RESEARCH PAPER", 1)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Intelligent Product Review Sentiment Analysis and Customer Feedback Classification Using Natural Language Processing and Machine Learning")
r.bold = True
r.font.size = Pt(16)
add_para(doc, "[Author Name]¹, [Co-author Name]²\n¹[Department], [Institution], [City], [Country]\n²[Department], [Institution], [City], [Country]\n[author]@[institution].edu", align=WD_ALIGN_PARAGRAPH.CENTER)

add_heading(doc, "Abstract", 1)
add_para(doc, "This paper describes a complete product-review sentiment system that classifies text as Positive, Negative, or Neutral and supplements textual opinion with rating mismatch analysis, bulk processing, product comparison, and aspect evidence extraction. The source data is the public Amazon Reviews 2023 All_Beauty category. Rating-derived weak labels define 1–2 as Negative, 3 as Neutral, and 4–5 as Positive. The implementation removes HTML and URLs, cleans text, removes duplicates, and uses a stratified 80/20 split before fitting a TF-IDF vectorizer. Four classical models—Logistic Regression, Multinomial Naive Bayes, Linear SVM, and Random Forest—were compared on 5,831 test reviews. Logistic Regression achieved accuracy 0.728177 and macro-F1 0.729387, making it the measured test winner. The project is deliberately transparent about weak supervision and the non-trained nature of heuristic emotion and aspect outputs.")
add_para(doc, "Index Terms—Aspect-based sentiment analysis, natural language processing, product reviews, TF-IDF, machine learning, Streamlit.")

add_heading(doc, "I. INTRODUCTION", 1)
add_para(doc, "Online customer reviews contain product satisfaction evidence, but they are voluminous and unstructured. A system must process review text, produce sentiment labels, compare those labels to numerical ratings, and explain which product attributes drive opinion. This work implements that pipeline while preserving reproducibility and academic integrity. The system accepts individual text, processes CSV files, analyzes configured aspects, and presents both measured model performance and business-oriented summaries.")

add_heading(doc, "II. RELATED WORK", 1)
add_para(doc, "Pang and Lee [1] established sentiment and opinion mining as a foundational computational problem. The supervised approach by Pang, Lee, and Vaithyanathan [2] showed that machine-learning classifiers can learn review polarity from text representations. Liu [3] distinguished overall, sentence-level, and aspect-level opinion analysis. Sebastiani [4] summarized supervised text categorization theory. Joachims [5] demonstrated support-vector machines for text classification, and Hutto and Gilbert [6] showed that domain-sensitive lexicons can provide practical polarity scores. Transformer-based methods [7] improve generalization through contextual representation learning, although classical TF-IDF methods remain useful, explainable baselines.")

add_heading(doc, "III. PROBLEM STATEMENT AND OBJECTIVES", 1)
add_para(doc, "The problem is to learn a map f: x → y from cleaned review text x to y ∈ {Positive, Negative, Neutral}. The project also requires confidence estimation, mismatch identification, aspect evidence, bulk processing, and product-level aggregation.")
add_para(doc, "The explicit objectives are: (i) prevent test leakage through split-before-vectorization, (ii) compare at least four classifiers, (iii) select a model using measured hold-out macro-F1, (iv) detect mixed opinions across aspects, and (v) present results in an interactive dashboard.")

add_heading(doc, "IV. PROPOSED METHODOLOGY", 1)
add_para(doc, "The source data were cleaned and weakly labeled before training. HTML tags and URLs were removed, text was lowercased, special characters were normalized, and duplicate normalized reviews were deleted. Negation words were retained. The 80/20 stratified split was performed before TF-IDF fitting. The fitted TF-IDF space used unigram/bigram features, sublinear term frequency, minimum document frequency two, and maximum 50,000 features.")

add_heading(doc, "V. SYSTEM ARCHITECTURE", 1)
add_para(doc, "Fig. 1 expresses the architecture: Dataset → Collection → Cleaning → TF-IDF → Split → Model Training → Sentiment Classification → Aspect and Rating Analysis → Dashboard → Business Insights. Separate modules implement preprocessing, training, prediction, and aspect extraction. Trained model and vectorizer artifacts are serialized in pickle format.")

add_heading(doc, "VI. DATASET AND PREPROCESSING", 1)
add_para(doc, "The public Amazon Reviews 2023 All_Beauty dataset provides rating, title, text, item identifiers, timestamp, verification status, and helpful votes [8]. The final processed project subset contains 29,153 rows after balancing, cleaning, and duplicate removal. The class counts are 9,845 Negative, 9,806 Neutral, and 9,502 Positive. These counts reflect rating-derived weak supervision, not expert annotations.")

add_heading(doc, "VII. ALGORITHMS", 1)
add_heading(doc, "A. Logistic Regression", 2)
add_para(doc, "Logistic Regression estimates class probabilities from a linear combination of TF-IDF features. Class weighting addresses relative class imbalance.")
add_heading(doc, "B. Multinomial Naive Bayes", 2)
add_para(doc, "Multinomial Naive Bayes applies a probabilistic word-count model under a conditional independence assumption.")
add_heading(doc, "C. Linear SVM", 2)
add_para(doc, "Linear SVM finds a maximum-margin boundary in TF-IDF feature space and supports class weighting.")
add_heading(doc, "D. Random Forest", 2)
add_para(doc, "Random Forest combines decision trees trained with bootstrap and feature randomness. It is included as a nonlinear ensemble baseline.")

add_heading(doc, "VIII. EXPERIMENTAL RESULTS AND DISCUSSION", 1)
t = doc.add_table(rows=1, cols=5)
t.style = "Table Grid"
for i, h in enumerate(["Model", "Accuracy", "Precision-M", "Recall-M", "F1-M"]):
    set_cell_text(t.rows[0].cells[i], h, True); set_cell_shading(t.rows[0].cells[i], "D9EAF7")
for _, row in results.iterrows():
    cells = t.add_row().cells
    vals = [row["model"], f"{row['accuracy']:.4f}", f"{row['precision_macro']:.4f}", f"{row['recall_macro']:.4f}", f"{row['f1_macro']:.4f}"]
    for i, value in enumerate(vals): set_cell_text(cells[i], value)
add_para(doc, "Table I. Actual hold-out results. M denotes macro averaging.")

add_para(doc, f"Logistic Regression achieved the highest macro-F1 result ({best['f1_macro']:.4f}) and accuracy ({best['accuracy']:.4f}). Multinomial Naive Bayes achieved F1 {results.iloc[1]['f1_macro']:.4f}, Linear SVM {results.iloc[2]['f1_macro']:.4f}, and Random Forest {results.iloc[3]['f1_macro']:.4f}. Per-class results show that Positive sentiment is the easiest class, while Neutral is consistently challenging. These results describe this weakly labeled hold-out subset only.")
add_para(doc, "The model is evaluated under fixed random seed 42. Accuracy is reported with macro precision, macro recall, macro F1, and confusion matrices to reduce the risk of misleading interpretation. ROC-AUC is additionally computed for models exposing class probabilities.")

add_heading(doc, "IX. ASPECT AND RATING ANALYSIS", 1)
add_para(doc, "Aspect terms cover quality, price, delivery, packaging, battery life, performance, design, and customer service. The analyzer divides text into clauses and compares positive and negative lexicon evidence around matching aspects. A mixed clause does not always permit a learned target-opinion assignment. Therefore, the feature is disclosed as lexicon-assisted rather than a trained ABSA model.")
add_para(doc, "The 1–5 rating is converted to the same weak sentiment label and compared with model output. A mismatch indicates disagreement worthy of review, not proof that a rating or text label is incorrect.")

add_heading(doc, "X. LIMITATIONS AND FUTURE WORK", 1)
add_para(doc, "Limitations include weak supervision, a single category, no expert aspect annotations, and heuristic emotion labels. Future work should collect human-labeled data, test cross-category and cross-platform transfer, add learned aspect extraction, compare DistilBERT, calibrate probabilities, monitor temporal drift, store analytics in SQLite/PostgreSQL, and deploy behind secure authentication.")

add_heading(doc, "XI. CONCLUSION", 1)
add_para(doc, "This work implemented a complete and reproducible product-review analytics platform. It combined public data, preprocessing, TF-IDF, four machine-learning baselines, hold-out evaluation, aspect evidence, rating mismatch detection, batch analysis, and an interactive dashboard. Logistic Regression was the empirically selected model. The project provides a transparent foundation for future expert-labeled and transformer-based research.")

add_heading(doc, "REFERENCES", 1)
refs = [
    "[1] B. Pang and L. Lee, “Opinion mining and sentiment analysis,” Foundations and Trends in Information Retrieval, vol. 2, no. 1–2, pp. 1–135, 2008.",
    "[2] B. Pang, L. Lee, and S. Vaithyanathan, “Thumbs up? Sentiment classification using machine learning techniques,” in Proc. EMNLP, 2002, pp. 79–86.",
    "[3] B. Liu, Sentiment Analysis and Opinion Mining. San Rafael, CA, USA: Morgan & Claypool, 2012.",
    "[4] F. Sebastiani, “Machine learning in automated text categorization,” ACM Computing Surveys, vol. 34, no. 1, pp. 1–47, 2002.",
    "[5] T. Joachims, “Text categorization with support vector machines: Learning with many relevant features,” in Proc. ECML, 1998, pp. 137–142.",
    "[6] C. J. Hutto and E. Gilbert, “VADER: A parsimonious rule-based model for sentiment analysis of social media text,” in Proc. ICWSM, 2014.",
    "[7] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training of deep bidirectional transformers for language understanding,” in Proc. NAACL-HLT, 2019, pp. 4171–4186.",
    "[8] Y. Hou et al., “Bridging language and items for retrieval and recommendation,” arXiv preprint arXiv:2403.03952, 2024. Dataset: McAuley-Lab/Amazon-Reviews-2023, https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023.",
]
for ref in refs:
    p = doc.add_paragraph(ref)
    p.paragraph_format.left_indent = Inches(0.2)

# FINAL APPENDIX
add_heading(doc, "AUTHOR DECLARATION", 1)
add_para(doc, "Author information, student names, institution names, roll numbers, academic year, guide details, and signatures must be entered in institutional format before final submission.")

# Core properties
props = doc.core_properties
props.title = "Complete Project Report and IEEE Paper — Product Review Sentiment Analysis"
props.subject = "NLP and Machine Learning Academic Project"
props.author = "[Author Name]"
props.keywords = "sentiment analysis, NLP, machine learning, product reviews, TF-IDF"

doc.save(OUT)
import shutil
shutil.copy2(OUT, ROOT_OUT)
print(OUT)
