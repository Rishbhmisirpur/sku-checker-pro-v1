import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from urllib.parse import urlparse

from scraper import get_html
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

# ---------------- SELLER FROM IMAGE URL ----------------
def extract_seller_from_url(url):
    try:
        if not url:
            return ""

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # domain based seller guess
        domain_map = {
            "amazon": "amazon",
            "flipkart": "flipkart",
            "myntra": "myntra",
            "ajio": "ajio",
            "nykaa": "nykaa"
        }

        for key, seller in domain_map.items():
            if key in domain:
                return seller

        # path based keyword extraction
        keywords = ["amazon", "flipkart", "myntra", "ajio", "nykaa"]
        for k in keywords:
            if k in path:
                return k

        return domain.split(".")[0]

    except:
        return ""

# ---------------- VERIFY ----------------
def verify(row):
    try:
        url = str(row.get("image_url", "")).strip()
        sku = str(row.get("product_sku", "")).strip()
        seller = str(row.get("product_seller", "")).strip()
        price_raw = row.get("product_price", "")

        if not url:
            return row.name, "Error", False, False, False, "", ""

        html = get_html(url)

        if not html:
            return row.name, "Error", False, False, False, "", ""

        # SKU
        sku_ok = ai_sku_match(html, sku) if use_ai else smart_sku_match(html, sku)

        # Seller from IMAGE URL (NEW LOGIC)
        found_seller = extract_seller_from_url(url)

        # Seller match
        seller_ok = smart_seller_match(found_seller, seller)

        # Price
        price = clean_price(price_raw)
        price_ok = price_match_for_seller(html, seller, price)

        result = classify_result(sku_ok, seller_ok, price_ok)

        expected = seller.lower().strip()
        found = found_seller.lower().strip()

        if sku_ok and expected and expected in found:
            exact_flag = "No"
            matched_seller = seller
        else:
            exact_flag = "Yes"
            matched_seller = found_seller if found_seller else ""

        return row.name, result, sku_ok, seller_ok, price_ok, matched_seller, exact_flag

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

            for i, f in enumerate(as_completed(futures)):
                results.append(f.result())
                progress.progress((i + 1) / len(df))

        # UPDATE RESULTS
        for idx, result, sku_ok, seller_ok, price_ok, matched_seller, exact_flag in results:
            df.loc[idx, "result"] = result
            df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
            df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
            df.loc[idx, "price_match"] = "Yes" if price_ok else "No"
            df.loc[idx, "matched_seller"] = matched_seller
            df.loc[idx, "exact_seller_not_match"] = exact_flag

        st.success("✅ Done")

        if st.toggle("🚨 Show Only Wrong Seller"):
            df = df[df["exact_seller_not_match"] == "Yes"]

        def highlight(row):
            return ["background-color: #ffcccc"] * len(row) if row["exact_seller_not_match"] == "Yes" else [""] * len(row)

        st.subheader("📋 Results")
        st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)

        show_metrics(df)
        show_chart(df)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            "result.csv"
        )
