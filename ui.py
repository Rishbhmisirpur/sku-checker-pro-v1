import streamlit as st
import pandas as pd
from matcher import match_sku

def run_ui():
    st.set_page_config(page_title="SKU Checker PRO", layout="wide")

    st.title("🔥 SKU Checker PRO MAX")

    # Sidebar
    st.sidebar.title("⚙ Settings")
    threads = st.sidebar.slider("Threads", 1, 20, 5)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", 0)
    col2.metric("Matched", 0)
    col3.metric("Failed", 0)
    col4.metric("Accuracy", "0%")

    # Upload
    file = st.file_uploader("📂 Upload CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)
        st.dataframe(df)

        if st.button("🚀 Start Checking"):

            results = []

            progress = st.progress(0)

            for i, row in df.iterrows():
                res = match_sku(row["sku"], row["url"])
                results.append(res)

                progress.progress((i+1)/len(df))

            result_df = pd.DataFrame(results)

            st.success("✅ Done")

            st.dataframe(result_df)

            st.download_button(
                "⬇ Download",
                result_df.to_csv(index=False),
                "result.csv"
            )
