import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import base64
from urllib.parse import urlparse, parse_qs

from playwright.sync_api import sync_playwright
from matcher import smart_sku_match, ai_sku_match, clean_price, price_match_for_seller
from utils import classify_result
from ui import show_metrics, show_chart


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
st.set_page_config(page_title="SKU Analyzer AI PRO", layout="wide")
st.title("🔥 SKU Analyzer AI PRO (UPGRADED)")

threads = st.sidebar.slider("Threads", 1, 5, 3)
use_ai = st.sidebar.toggle("🤖 AI SKU Matching")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])


# ---------------- URL DECODER ----------------
def decode_url(url):
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        if "page_link" in qs:
            return base64.b64decode(qs["page_link"][0]).decode("utf-8")

        return url
    except:
        return url


# ---------------- NORMALIZE ----------------
def normalize(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


# ---------------- REAL BROWSER SCRAPER ----------------
def get_page_content(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="networkidle", timeout=60000)

            html = page.content()

            browser.close()

            return html
    except:
        return ""


# ---------------- SELLER EXTRACTION (BROWSER BASED) ----------------
def extract_seller(html):
    html = html.lower()

    patterns = [
        r"mitzi at ([a-z0-9\s\-&]+)",
        r"sold by[:\s]*([a-z0-9\s\-&]+)",
        r"merchant[:\s]*([a-z0-9\s\-&]+)",
        r"brand[:\s]*([a-z0-9\s\-&]+)",
        r"lighting new york",
        r"wayfair",
        r"lumens",
        r"ferguson"
    ]

    sellers = set()

    for p in patterns:
        matches = re.findall(p, html)
        for m in matches:
            sellers.add(normalize(m))

    return list(sellers)


# ---------------- SMART MATCH ----------------
def seller_match(html, sheet_seller):
    sheet = normalize(sheet_seller)
    sellers = extract_seller(html)

    for s in sellers:
        if not s:
            continue

        if sheet in s or s in sheet:
            return True

        if len(set(sheet.split()) & set(s.split())) >= 2:
            return True

    return False


# ---------------- VERIFY ----------------
def verify(row):
    try:
        url = str(row.get("image_url", "")).strip()
        sku = str(row.get("product_sku", "")).strip()
        seller = str(row.get("product_seller", "")).strip()
        price_raw = row.get("product_price", "")

        if not url:
            return row.name, "Error", False, False, False, "", ""

        real_url = decode_url(url)

        # 🔥 REAL BROWSER LOAD
        html = get_page_content(real_url)

        if not html:
            return row.name, "Error", False, False, False, "", ""

        # SKU
        sku_ok = ai_sku_match(html, sku) if use_ai else smart_sku_match(html, sku)

        # SELLER (REAL FIX)
        seller_ok = seller_match(html, seller)

        # PRICE
        price = clean_price(price_raw)
        price_ok = price_match_for_seller(html, seller, price)

        result = classify_result(sku_ok, seller_ok, price_ok)

        matched_seller = "MATCHED" if seller_ok else "NO MATCH"
        exact_flag = "No" if seller_ok else "Yes"

        return row.name, result, sku_ok, seller_ok, price_ok, matched_seller, exact_flag

    except Exception as e:
        return row.name, f"Error: {str(e)}", False, False, False, "", ""


# ---------------- MAIN ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Preview")
    st.dataframe(df.head())

    if st.button("🚀 Start Check (UPGRADED ENGINE)"):

        progress = st.progress(0)
        results = []

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(verify, row) for _, row in df.iterrows()]

            for i, f in enumerate(as_completed(futures)):
                results.append(f.result())
                progress.progress((i + 1) / len(df))

        # UPDATE
        for idx, result, sku_ok, seller_ok, price_ok, matched_seller, exact_flag in results:
            df.loc[idx, "result"] = result
            df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
            df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
            df.loc[idx, "price_match"] = "Yes" if price_ok else "No"
            df.loc[idx, "matched_seller"] = matched_seller
            df.loc[idx, "exact_seller_not_match"] = exact_flag

        st.success("✅ UPGRADED ENGINE DONE")

        def highlight(row):
            return ["background-color: #ffcccc"] * len(row) if row["exact_seller_not_match"] == "Yes" else [""] * len(row)

        st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)

        show_metrics(df)
        show_chart(df)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            "result.csv"
        )
