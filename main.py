import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import get_html
from matcher import smart_sku_match, smart_seller_match, clean_price, price_match_for_seller
from utils import classify_result
from ui import show_metrics, show_chart

st.set_page_config(page_title="SKU Analyzer PRO", layout="wide")

# 🎨 Title
st.markdown("## 🔥 SKU Analyzer PRO Dashboard")

# 📂 Upload Section
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# Tabs
tab1, tab2, tab3 = st.tabs(["📂 Upload", "📊 Results", "📈 Analytics"])

# 🔍 Core Function
def verify(row):
    try:
        url = str(row["url"]).strip()
        html = get_html(url)

        if not html:
            return row.name, "Error", False, False, False

        sku_ok = smart_sku_match(html, row["sku"])
        seller_ok = smart_seller_match(html, row["seller"])
        price = clean_price(row["price"])
        price_ok = price_match_for_seller(html, row["seller"], price)

        result = classify_result(sku_ok, seller_ok, price_ok)

        return row.name, result, sku_ok, seller_ok, price_ok

    except Exception as e:
        return row.name, "Error", False, False, False


# =========================
# 📂 TAB 1: Upload + Process
# =========================
with tab1:
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.write("Preview:")
        st.dataframe(df.head())

        workers = st.slider("⚙️ Threads", 1, 10, 5)

        if st.button("🚀 Start Check"):
            progress = st.progress(0)
            status = st.empty()

            results = []

            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(verify, row) for _, row in df.iterrows()]

                for i, future in enumerate(as_completed(futures)):
                    idx, result, sku_ok, seller_ok, price_ok = future.result()

                    results.append((idx, result, sku_ok, seller_ok, price_ok))

                    status.text(f"Processing {i+1}/{len(df)}")
                    progress.progress((i + 1) / len(df))

            # Update DF safely
            for idx, result, sku_ok, seller_ok, price_ok in results:
                df.loc[idx, "result"] = result
                df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
                df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
                df.loc[idx, "price_match"] = "Yes" if price_ok else "No"

            st.session_state["df"] = df
            st.success("✅ Processing Completed")


# =========================
# 📊 TAB 2: Results + Filters
# =========================
with tab2:
    if "df" in st.session_state:
        df = st.session_state["df"]

        st.subheader("🔎 Filters")

        col1, col2 = st.columns(2)

        with col1:
            result_filter = st.multiselect("Result", df["result"].unique())

        with col2:
            seller_filter = st.multiselect("Seller", df["seller"].unique())

        filtered_df = df.copy()

        if result_filter:
            filtered_df = filtered_df[filtered_df["result"].isin(result_filter)]

        if seller_filter:
            filtered_df = filtered_df[filtered_df["seller"].isin(seller_filter)]

        st.subheader("📋 Results Table")
        st.dataframe(filtered_df, use_container_width=True)

        st.download_button(
            "📥 Download Filtered CSV",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "filtered_results.csv"
        )


# =========================
# 📈 TAB 3: Analytics
# =========================
with tab3:
    if "df" in st.session_state:
        df = st.session_state["df"]

        st.subheader("📊 Metrics")
        show_metrics(df)

        st.subheader("📈 Charts")
        show_chart(df)
