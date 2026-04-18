import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import fetch_html
from matcher import verify_row
from ui import render_row, render_result
from db import init_db, save_result

st.set_page_config(page_title="SKU Checker PRO MAX", layout="wide")
st.title("🔥 SKU + Seller + Price Analyzer")

init_db()

file = st.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)

    if st.button("🚀 Start Check"):

        progress = st.progress(0)
        placeholder = st.empty()
        done = 0

        results = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(verify_row, row) for _, row in df.iterrows()]

            for f in as_completed(futures):
                res = f.result()
                results.append(res)

                idx = res["index"]
                df.loc[idx, "result"] = res["result"]
                df.loc[idx, "sku_match"] = res["sku"]
                df.loc[idx, "seller_match"] = res["seller"]
                df.loc[idx, "price_match"] = res["price"]

                save_result(res)

                done += 1
                progress.progress(done / len(df))

                render_row(df)

        render_result(df)
