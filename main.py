# main.py
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


def verify(row):
    url = row.get("image_url")
    sku = row.get("product_sku")
    seller = row.get("product_seller")
    price = row.get("product_price")

    html = get_html(url)

    sku_ok = sku_match(html, sku)
    seller_ok = seller_match(html, seller)
    price_ok = price_match(html, price)

    result = classify(sku_ok, seller_ok, price_ok)

    save_result(sku, seller, price, result)

    return {
        "sku": sku,
        "seller": seller,
        "price": price,
        "result": result
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

        show_metrics(out)
        show_chart(out)

        st.download_button("Download", out.to_csv(index=False), "result.csv")
