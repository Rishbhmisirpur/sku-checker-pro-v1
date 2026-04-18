import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import get_html
from matcher import smart_sku_match, smart_seller_match, clean_price, price_match_for_seller
from utils import classify_result
from ui import show_metrics, show_chart

# ---------------- CONFIG ----------------
st.set_page_config(page_title="SKU Analyzer PRO", layout="wide")
st.title("🔥 SKU Analyzer PRO")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# ---------------- VERIFY FUNCTION ----------------
def verify(row):
    try:
        url = str(row.get("url", "")).strip()
        sku = str(row.get("sku", "")).strip()
        seller = str(row.get("seller", "")).strip()
        price_raw = row.get("price", "")

        if not url:
            return row.name, "Error", False, False, False

        html = get_html(url)

        if not html:
            return row.name, "Error", False, False, False

        sku_ok = smart_sku_match(html, sku)
        seller_ok = smart_seller_match(html, seller)

        price = clean_price(price_raw)
        price_ok = price_match_for_seller(html, seller, price)

        result = classify_result(sku_ok, seller_ok, price_ok)

        return row.name, result, sku_ok, seller_ok, price_ok

    except Exception as e:
        return row.name, "Error", False, False, False


# ---------------- MAIN ----------------
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error("❌ CSV read error")
        st.stop()

    # Required columns check
    required_cols = ["url", "sku", "seller", "price"]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        st.error(f"❌ Missing columns: {missing}")
        st.stop()

    st.subheader("📊 Preview")
    st.dataframe(df.head(), use_container_width=True)

    workers = st.slider("Threads", 1, 10, 5)

    if st.button("🚀 Start Check"):
        progress = st.progress(0)
        status = st.empty()

        results = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(verify, row) for _, row in df.iterrows()]

            for i, future in enumerate(as_completed(futures)):
                idx, result, sku_ok, seller_ok, price_ok = future.result()

                results.append((idx, result, sku_ok, seller_ok, price_ok))

                progress.progress((i + 1) / len(df))
                status.text(f"Processing {i+1}/{len(df)}")

        # Safe update
        for idx, result, sku_ok, seller_ok, price_ok in results:
            df.loc[idx, "result"] = result
            df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
            df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
            df.loc[idx, "price_match"] = "Yes" if price_ok else "No"

        st.success("✅ Completed")

        # ---------------- OUTPUT ----------------
        show_metrics(df)
        show_chart(df)

        st.subheader("📋 Results")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            "results.csv"
        )
