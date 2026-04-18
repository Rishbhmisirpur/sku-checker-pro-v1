import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

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

threads = st.sidebar.slider("Threads", 1, 10, 5)
use_ai = st.sidebar.toggle("🤖 AI Matching")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# 🔍 SELLER EXTRACT
def extract_seller_name(html, expected_seller):
    try:
        if expected_seller.lower() in html.lower():
            return expected_seller
        return ""
    except:
        return ""

# ---------------- VERIFY ----------------
def verify(row):
    try:
        # 🔥 NEW COLUMN NAMES USE
        url = str(row.get("image_url", "")).strip()
        sku = str(row.get("product_sku", "")).strip()
        seller = str(row.get("product_seller", "")).strip()
        price_raw = row.get("product_price", "")

        if not url:
            return row.name, "Error: URL Missing", False, False, False, "", ""

        html = get_html(url)

        if not html or len(html) < 50:
            return row.name, "Error: Page Not Loaded", False, False, False, "", ""

        # 🔥 SKU MATCH
        if use_ai:
            sku_ok = ai_sku_match(html, sku)
        else:
            sku_ok = smart_sku_match(html, sku)

        # 🔥 SELLER MATCH
        seller_ok = smart_seller_match(html, seller)

        # 🔥 PRICE MATCH
        price = clean_price(price_raw)
        price_ok = price_match_for_seller(html, seller, price)

        # 🔥 IMAGE
        image = extract_image(html) or ""

        # 🔥 SELLER FOUND
        found_seller = extract_seller_name(html, seller) or ""

        # 🔥 RESULT
        result = classify_result(sku_ok, seller_ok, price_ok)

        return row.name, result, sku_ok, seller_ok, price_ok, image, found_seller

    except Exception as e:
        return row.name, f"Error: {str(e)}", False, False, False, "", ""

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
                idx, result, sku_ok, seller_ok, price_ok, image, found_seller = future.result()

                results.append((idx, result, sku_ok, seller_ok, price_ok, image, found_seller))
                progress.progress((i + 1) / len(df))

     for ...
    df.loc[...] ✅, result, sku_ok, seller_ok, price_ok, image, found_seller in results:
    df.loc[idx, "result"] = result
    df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
    df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
    df.loc[idx, "price_match"] = "Yes" if price_ok else "No"
    df.loc[idx, "matched_seller"] = found_seller

    # 🔥 exact seller check
    if sku_ok:
        if str(found_seller).strip().lower() == str(df.loc[idx, "product_seller"]).strip().lower():
            df.loc[idx, "exact_seller_not_match"] = "No"
        else:
            df.loc[idx, "exact_seller_not_match"] = "Yes"
    else:
        df.loc[idx, "exact_seller_not_match"] = "No"

st.success("✅ Done")

        # 🔥 rename columns
        df.rename(columns={
            "sku": "product_sku",
            "url": "image_url",
            "seller": "product_seller",
            "price": "product_price"
        }, inplace=True)

        # 🚨 filter toggle
        show_wrong = st.toggle("🚨 Show Only Wrong Seller")

        if show_wrong:
            df = df[df["exact_seller_not_match"] == "Yes"]

        # 🎨 highlight
        def highlight_rows(row):
            if row["exact_seller_not_match"] == "Yes":
                return ["background-color: #ffcccc"] * len(row)
            return [""] * len(row)

        st.subheader("📋 Results")
        st.dataframe(df.style.apply(highlight_rows, axis=1), use_container_width=True)

        show_metrics(df)
        show_chart(df)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            "result.csv"
        )
