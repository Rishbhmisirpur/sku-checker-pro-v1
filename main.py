import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from scraper import get_html
from matcher import sku_match, seller_match, price_match, classify
from db import init_db, save_result
from ui import chat_support, show_metrics, show_chart

init_db()

st.set_page_config(layout="wide")
st.title("🚀 SKU SYSTEM")

chat_support()

file = st.file_uploader("Upload CSV")


def verify(row):
    url = row["image_url"]
    sku = row["product_sku"]
    seller = row["product_seller"]
    price = row["product_price"]

    html = get_html(url)

    if not html:
        return {
            "sku": sku,
            "seller": seller,
            "price": price,
            "sku_match": "No",
            "seller_match": "No",
            "price_match": "No",
            "final_result": "NO"
        }

    sku_ok = sku_match(html, sku)
    seller_ok = seller_match(html, seller)
    price_ok = price_match(html, price, seller)

    result = classify(sku_ok, seller_ok, price_ok)

    save_result(sku, seller, price, result)

    return {
        "sku": sku,
        "seller": seller,
        "price": price,
        "sku_match": "Yes" if sku_ok else "No",
        "seller_match": "Yes" if seller_ok else "No",
        "price_match": "Yes" if price_ok else "No",
        "final_result": result
    }


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

        st.download_button(
            "Download CSV",
            out.to_csv(index=False),
            "result.csv"
        )
