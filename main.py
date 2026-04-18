import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import get_html
from matcher import sku_match, seller_match, price_match, ai_sku_match, classify
from db import save_result
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
        st.sidebar.error("Invalid")


if not st.session_state.login:
    st.stop()


# ---------------- UI ----------------
st.title("🚀 AI SKU PRO SAAS SYSTEM")

chat_support()

file = st.file_uploader("Upload CSV")


def verify(row):
    url = row.get("image_url")
    sku = row.get("product_sku")
    seller = row.get("product_seller")
    price = row.get("product_price")

    html = get_html(url)

    sku_ok = ai_sku_match(html, sku)
    seller_ok = seller_match(html, seller)
    price_ok = price_match(html, price)

    result = classify(sku_ok, seller_ok, price_ok)

    save_result(sku, seller, price, result)

    return result


if file:
    df = pd.read_csv(file)

    if st.button("RUN ENGINE"):
        results = []

        with ThreadPoolExecutor(max_workers=5) as ex:
            futures = [ex.submit(verify, r) for _, r in df.iterrows()]

            for f in futures:
                results.append(f.result())

        df["result"] = results

        st.dataframe(df)

        show_metrics(df)
        show_chart(df)

        st.download_button("Download", df.to_csv(index=False), "result.csv")
