import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from aspect_analysis import analyze_aspects
from predict import predict_review

st.set_page_config(page_title="Product Review Intelligence", page_icon="🛍️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
div[data-testid="stMetric"] {background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;}
</style>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", [
    "Home", "Single Review", "Bulk Analysis", "Product Analytics",
    "Product Comparison", "Aspect Analysis", "Model Performance"
])

st.sidebar.caption("TF-IDF + Logistic Regression")

if page == "Home":
    st.title("Intelligent Product Review Sentiment Analysis")
    st.markdown("Analyze customer opinions, satisfaction, mismatches, product attributes, and model performance.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sentiment Classes", "3", "Positive / Neutral / Negative")
    c2.metric("Dataset", "Amazon Reviews 2023", "All_Beauty category")
    c3.metric("Technology", "Python + Streamlit", "Industry dashboard")

    st.subheader("Project objectives")
    st.write("• Predict sentiment and confidence for individual or uploaded reviews")
    st.write("• Compare star ratings against written opinion")
    st.write("• Compare product review distributions and satisfaction")
    st.write("• Surface frequent aspects and improvement areas")

elif page == "Single Review":
    st.header("Single Review Analysis")
    review = st.text_area("Enter a product review", height=180,
                          placeholder="The phone has an excellent camera, but its battery life is terrible.")
    rating = st.selectbox("Optional star rating", [None, 1, 2, 3, 4, 5])
    if st.button("Analyze Review", type="primary"):
        if review.strip():
            sentiment, confidence, emotion = predict_review(review)
            a, b, c = st.columns(3)
            a.metric("Predicted Sentiment", sentiment)
            b.metric("Confidence", f"{confidence:.1%}" if confidence is not None else "Not available")
            c.metric("Detected Emotion", emotion)

            if rating is not None:
                rating_sentiment = "Negative" if rating <= 2 else "Neutral" if rating == 3 else "Positive"
                mismatch = sentiment != rating_sentiment
                st.info("Rating and sentiment match." if not mismatch else
                        f"Mismatch detected: rating suggests {rating_sentiment}, but text predicts {sentiment}.")

            st.subheader("Aspect opinions")
            aspects = analyze_aspects(review)
            if aspects:
                st.dataframe(pd.DataFrame(aspects).T.reset_index(names="Aspect"), use_container_width=True)
            else:
                st.write("No configured aspect terms were detected.")
        else:
            st.warning("Please enter review text.")

elif page == "Bulk Analysis":
    st.header("Bulk Review Analysis")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        text_col = "text" if "text" in df.columns else "review_text" if "review_text" in df.columns else None
        if text_col:
            from preprocessing import clean_review
            df["clean_text"] = df[text_col].fillna("").apply(clean_review)
            predictions = []
            confidences = []
            emotions = []
            for text in df["clean_text"]:
                pred, conf, emotion = predict_review(text)
                predictions.append(pred)
                confidences.append(conf)
                emotions.append(emotion)
            df["Predicted_Sentiment"] = predictions
            df["Confidence"] = confidences
            df["Detected_Emotion"] = emotions
            st.dataframe(df, use_container_width=True)
            st.download_button("Download analyzed CSV", df.to_csv(index=False),
                               "analyzed_reviews.csv", "text/csv")
            fig = px.histogram(df, x="Predicted_Sentiment", color="Predicted_Sentiment",
                               title="Bulk Sentiment Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("CSV must contain a 'text' or 'review_text' column.")

elif page == "Product Analytics":
    st.header("Product Analytics")
    data_path = ROOT / "data" / "processed" / "processed_reviews.csv"
    if not data_path.exists():
        st.warning("Processed dataset not found. Run src/train_models.py first.")
    else:
        df = pd.read_csv(data_path)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Reviews", f"{len(df):,}")
        c2.metric("Positive", f"{(df['sentiment']=='Positive').mean():.1%}")
        c3.metric("Negative", f"{(df['sentiment']=='Negative').mean():.1%}")
        c4.metric("Average Rating", f"{df['rating'].mean():.2f}")
        fig = px.pie(df, names="sentiment", title="Sentiment Distribution",
                     color="sentiment", color_discrete_map={"Positive":"#16a34a", "Neutral":"#f59e0b", "Negative":"#dc2626"})
        st.plotly_chart(fig, use_container_width=True)

elif page == "Product Comparison":
    st.header("Product Comparison")
    data_path = ROOT / "data" / "processed" / "processed_reviews.csv"
    if data_path.exists():
        df = pd.read_csv(data_path)
        product_col = "parent_asin" if "parent_asin" in df.columns else "asin"
        choices = df[product_col].dropna().astype(str).unique().tolist()[:500]
        selected = st.multiselect("Select up to products", choices, default=choices[:2], max_selections=5)
        if selected:
            comparison = df[df[product_col].astype(str).isin(selected)].groupby(product_col).agg(
                Reviews=("clean_text", "count"), Average_Rating=("rating", "mean")
            ).reset_index()
            sentiment = df[df[product_col].astype(str).isin(selected)].groupby([product_col, "sentiment"]).size().groupby(level=0).apply(lambda x: 100*x/x.sum()).rename("percentage").reset_index()
            sentiment.columns = [product_col, "Sentiment", "Percentage"]
            c1, c2 = st.columns(2)
            c1.dataframe(comparison, use_container_width=True)
            c2.plotly_chart(px.bar(sentiment, x=product_col, y="Percentage", color="Sentiment",
                                   barmode="group", title="Sentiment Comparison"), use_container_width=True)
    else:
        st.warning("Processed dataset not found.")

elif page == "Aspect Analysis":
    st.header("Aspect-Based Sentiment Analysis")
    text = st.text_area("Enter review text for aspect extraction", height=160,
                        value="The phone has excellent camera quality but terrible battery life.")
    if st.button("Extract Aspects"):
        result = analyze_aspects(text)
        if result:
            rows = [{"Aspect": aspect, **values} for aspect, values in result.items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
            fig = px.bar(pd.DataFrame(rows), x="Aspect", y=["positive_evidence", "negative_evidence"],
                         barmode="group", title="Positive vs Negative Aspect Evidence")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No configured product aspects were found.")

elif page == "Model Performance":
    st.header("Model Performance")
    result_path = ROOT / "reports" / "model_evaluation_results.csv"
    if result_path.exists():
        results = pd.read_csv(result_path)
        st.dataframe(results, use_container_width=True)
        st.plotly_chart(px.bar(results, x="model", y="f1_macro", range_y=[0, 1],
                               title="Macro F1-score Comparison"), use_container_width=True)
        for model in results["model"]:
            slug = model.lower().replace(" ", "_")
            image = ROOT / "reports" / f"confusion_{slug}.png"
            if image.exists():
                st.subheader(f"{model} Confusion Matrix")
                st.image(str(image), use_column_width=True)
    else:
        st.warning("Evaluation files not found. Run src/train_models.py first.")
