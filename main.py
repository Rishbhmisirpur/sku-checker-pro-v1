import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import get_html
from matcher import smart_sku_match, smart_seller_match, clean_price, price_match_for_seller
from utils import classify_result
from ui import show_metrics, show_chart

st.set_page_config(page_title="SKU Analyzer PRO", layout="wide")
st.title("🔥 SKU Analyzer PRO")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

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

    except:
        return row.name, "Error", False, False, False

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if st.button("🚀 Start Check"):
        progress = st.progress(0)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(verify, row) for _, row in df.iterrows()]

            for i, future in enumerate(as_completed(futures)):
                idx, result, sku_ok, seller_ok, price_ok = future.result()

                df.loc[idx, "result"] = result
                df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
                df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
                df.loc[idx, "price_match"] = "Yes" if price_ok else "No"

                progress.progress((i + 1) / len(df))

        st.success("✅ Completed")

        show_metrics(df)
        show_chart(df)

        st.dataframe(df)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            "result.csv"
        )
