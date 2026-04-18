import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import re
import base64
import requests
import random
import math
from urllib.parse import urlparse, parse_qs

# ✅ DB INIT (IMPORTANT FIX)
from db import init_db, save_result
init_db()

from matcher import sku_match, seller_match, price_match, ai_sku_match, classify
from scraper import get_html
from ui import chat_support, show_metrics, show_chart


# ---------------- LOGIN ----------------
st.set_page_config(layout="wide")

if "login" not in st.session_state:
    st.session_state.login = False

st.sidebar.title("🔐 LOGIN")

user = st.sidebar.text_input("User")
pwd = st.sidebar.text_input("Pass", type="password")

if st.sidebar.button("Login"):
    if user == "admin" and pwd == "1234":
        st.session_state.login = True
    elif user == "guest":
        st.session_state.login = True
    else:
        st.sidebar.error("Invalid login")


if not st.session_state.login:
    st.stop()


# ---------------- UI ----------------
st.title("🚀 AI SKU PRO - FINAL STABLE SYSTEM")

chat_support()

file = st.file_uploader("Upload CSV")


# ---------------- URL DECODE ----------------
def decode_url(url):
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        if "page_link" in qs:
            return base64.b64decode(qs["page_link"][0]).decode("utf-8")

        return url
    except:
        return url


# ---------------- VERIFY FUNCTION ----------------
def verify(row):
    url = row.get("image_url")
    sku = row.get("product_sku")
    seller = row.get("product_seller")
    price = row.get("product_price")

    real_url = decode_url(url)
    html = get_html(real_url)

    sku_ok = ai_sku_match(html, sku)
    seller_ok = seller_match(html, seller)
    price_ok = price_match(html, price)

    result = classify(sku_ok, seller_ok, price_ok)

    # ✅ DB SAVE (NOW SAFE AFTER INIT FIX)
    save_result(sku, seller, price, result)

    return {
        "sku": sku,
        "seller": seller,
        "price": price,
        "result": result,
        "sku_ok": sku_ok,
        "seller_ok": seller_ok,
        "price_ok": price_ok
    }


# ---------------- MAIN ----------------
if file:
    df = pd.read_csv(file)

    st.subheader("📊 Preview")
    st.dataframe(df.head())

    if st.button("🚀 RUN FINAL ENGINE"):

        results = []

        with ThreadPoolExecutor(max_workers=5) as ex:
            futures = [ex.submit(verify, r) for _, r in df.iterrows()]

            for f in futures:
                results.append(f.result())

        # convert back to df
        out = pd.DataFrame(results)

        st.success("🔥 PROCESS COMPLETE")

        st.dataframe(out)

        show_metrics(out)
        show_chart(out)

        st.download_button(
            "📥 Download CSV",
            out.to_csv(index=False),
            "result.csv"
        )
