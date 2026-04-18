import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from scraper import get_html
from matcher import sku_match, seller_match, price_match, classify
from db import init_db, save_result
from ui import chat_support, show_metrics, show_chart

init_db()

st.set_page_config(layout="wide")
st.title("🚀 FINAL SKU VERIFICATION SYSTEM")

chat_support()

file = st.file_uploader("Upload CSV")


# ---------------- VERIFY ----------------
def verify(row):
    url = row.get("image_url")
    sku = row.get("product_sku")
    seller = row.get("product_seller")
    price = row.get("product_price")

    html = get_html(url)

    sku_ok = sku_match(html, sku)
    seller_ok = seller_match(html, seller)
    price_ok = price_match(html, price)

    final_result = classify(sku_ok, seller_ok, price_ok)

    # DB SAVE
    save_result(sku, seller, price, final_result)

    return {
        "sku_match": "Yes" if sku_ok else "No",
        "seller_match": "Yes" if seller_ok else "No",
        "price_match": "Yes" if price_ok else "No",
        "final_result": final_result
    }


# ---------------- RUN ----------------
if file:
    df = pd.read_csv(file)

    if st.button("RUN"):
        results = []

        with ThreadPoolExecutor(max_workers=5) as ex:
            futures = [ex.submit(verify, r) for _, r in df.iterrows()]

            for f in futures:
                results.append(f.result())

        out = pd.DataFrame(results)

        st.dataframe(out)

        show_metrics(out)
        show_chart(out)

        st.download_button(
            "Download CSV",
            out.to_csv(index=False),
            "result.csv"
        )
