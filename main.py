import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import get_html, extract_image
from matcher import smart_sku_match, smart_seller_match, clean_price, price_match_for_seller, ai_sku_match
from utils import classify_result
from ui import show_metrics, show_chart

# 🔐 LOGIN
def login():
    st.title("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid login")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ---------------- UI ----------------
st.set_page_config(page_title="SKU Analyzer AI PRO", layout="wide")
st.title("🔥 SKU Analyzer AI PRO")

# Sidebar
threads = st.sidebar.slider("Threads", 1, 10, 5)
use_ai = st.sidebar.toggle("🤖 AI Matching")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# ---------------- VERIFY ----------------
def verify(row):
    try:
        url = str(row.get("url", "")).strip()
        sku = str(row.get("sku", "")).strip()
        seller = str(row.get("seller", "")).strip()
        price_raw = row.get("price", "")

        html = get_html(url)

        if not html:
            return row.name, "Error", False, False, False, ""

        if use_ai:
            sku_ok = ai_sku_match(html, sku)
        else:
            sku_ok = smart_sku_match(html, sku)

        seller_ok = smart_seller_match(html, seller)
        price = clean_price(price_raw)
        price_ok = price_match_for_seller(html, seller, price)

        image = extract_image(html)

        result = classify_result(sku_ok, seller_ok, price_ok)

        return row.name, result, sku_ok, seller_ok, price_ok, image

    except:
        return row.name, "Error", False, False, False, ""


# ---------------- MAIN ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Preview")
    st.dataframe(df.head())

    if st.button("🚀 Start Check"):
        progress = st.progress(0)
        results = []

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(verify, row) for _, row in df.iterrows()]

            for i, future in enumerate(as_completed(futures)):
                idx, result, sku_ok, seller_ok, price_ok, image = future.result()

                results.append((idx, result, sku_ok, seller_ok, price_ok, image))
                progress.progress((i + 1) / len(df))

        for idx, result, sku_ok, seller_ok, price_ok, image in results:
            df.loc[idx, "result"] = result
            df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
            df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
            df.loc[idx, "price_match"] = "Yes" if price_ok else "No"
            df.loc[idx, "image"] = image

        st.success("✅ Done")

        # 🔥 COLUMN RENAME (FINAL OUTPUT)
        df.rename(columns={
            "sku": "product_sku",
            "url": "image_url",
            "seller": "product_seller",
            "price": "product_price"
        }, inplace=True)

        # 🔥 COLUMN ORDER FIX
        final_cols = [
            "product_sku",
            "image_url",
            "product_seller",
            "product_price",
            "image",
            "result",
            "sku_match",
            "seller_match",
            "price_match"
        ]

        df = df[[col for col in final_cols if col in df.columns]]

        show_metrics(df)
        show_chart(df)

        st.subheader("📋 Results")
        st.dataframe(df)

        # 🖼️ IMAGE PREVIEW
        if "image" in df.columns:
            st.subheader("🖼️ Image Preview")
            st.image(df["image"].dropna().head(5).tolist(), width=120)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            "result.csv"
        )
