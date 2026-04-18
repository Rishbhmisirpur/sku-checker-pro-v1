import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import base64
import requests
import random
import math
from urllib.parse import urlparse, parse_qs


# ---------------- LOGIN ----------------
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
st.set_page_config(page_title="SKU Analyzer FINAL", layout="wide")
st.title("🔥 SKU Analyzer AI PRO (FINAL WORKING)")

threads = st.sidebar.slider("Threads", 1, 10, 5)

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])


# ---------------- SESSION ----------------
session = requests.Session()


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


# ---------------- HTML FETCH ----------------
def get_html(url):
    try:
        headers_list = [
            {"User-Agent": "Mozilla/5.0 Chrome"},
            {"User-Agent": "Mozilla/5.0 Firefox"},
            {"User-Agent": "Mozilla/5.0 Safari"},
        ]

        for _ in range(3):
            headers = random.choice(headers_list)
            r = session.get(url, headers=headers, timeout=25)
            html = r.text or ""

            if len(html) > 150:
                return html

        return ""

    except:
        return ""


# ---------------- CLEAN ----------------
def clean(text):
    if not text:
        return ""
    return str(text).lower().strip()


# ---------------- SKU MATCH ----------------
def sku_match(html, sku):
    if not html or not sku:
        return False

    html = html.lower()
    sku = clean(sku)

    if sku in html:
        return True

    sku_nums = re.findall(r"\d+", sku)
    html_nums = re.findall(r"\d+", html)

    if sku_nums and html_nums:
        if sku_nums[0] in html_nums:
            return True

    sku_tokens = set(sku.split())
    html_tokens = set(re.findall(r"[a-z0-9]+", html))

    return len(sku_tokens & html_tokens) >= 1


# ---------------- SELLER MATCH ----------------
def seller_match(html, seller):
    if not html or not seller:
        return False

    html = html.lower()
    seller = clean(seller).replace(".com", "").replace("www", "")

    if seller in html:
        return True

    seller_tokens = set(seller.split())
    html_tokens = set(re.findall(r"[a-z0-9]+", html))

    return len(seller_tokens & html_tokens) >= 1


# ---------------- PRICE MATCH ----------------
def price_match(html, price):
    try:
        if not html or not price:
            return False

        price = float(re.sub(r"[^0-9.]", "", str(price)))

        html_prices = re.findall(r"\d+\.?\d*", html)
        html_prices = [float(p) for p in html_prices if p.replace(".", "").isdigit()]

        for p in html_prices:
            if math.isclose(p, price, rel_tol=0.05):
                return True

        return False

    except:
        return False


# ---------------- CLASSIFIER (INLINE FIX) ----------------
def classify_result(sku_ok, seller_ok, price_ok):
    if sku_ok and seller_ok and price_ok:
        return "Perfect Match"
    elif sku_ok and seller_ok:
        return "Partial Match"
    elif sku_ok:
        return "SKU Only"
    else:
        return "No Match"


# ---------------- VERIFY ----------------
def verify(row):
    try:
        url = str(row.get("image_url", "") or "").strip()
        sku = str(row.get("product_sku", "") or "").strip()
        seller = str(row.get("product_seller", "") or "").strip()
        price = row.get("product_price", "")

        if not url:
            return row.name, "Missing URL", False, False, False

        real_url = decode_url(url)
        html = get_html(real_url)

        if not html:
            return row.name, "No HTML", False, False, False

        sku_ok = sku_match(html, sku)
        seller_ok = seller_match(html, seller)
        price_ok = price_match(html, price)

        result = classify_result(sku_ok, seller_ok, price_ok)

        return row.name, result, sku_ok, seller_ok, price_ok

    except:
        return row.name, "Error Safe", False, False, False


# ---------------- MAIN ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Preview")
    st.dataframe(df.head())

    if st.button("🚀 START CHECK"):

        progress = st.progress(0)
        results = []

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(verify, row) for _, row in df.iterrows()]

            for i, f in enumerate(as_completed(futures)):
                results.append(f.result())
                progress.progress((i + 1) / len(df))

        for idx, result, sku_ok, seller_ok, price_ok in results:
            df.loc[idx, "result"] = result
            df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
            df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
            df.loc[idx, "price_match"] = "Yes" if price_ok else "No"

        st.success("🔥 FINAL FIX COMPLETE")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            "result.csv"
        )
