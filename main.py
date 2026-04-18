import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import base64
import requests
from urllib.parse import urlparse, parse_qs

from matcher import smart_sku_match, ai_sku_match, clean_price, price_match_for_seller
from utils import classify_result


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
st.set_page_config(page_title="SKU Analyzer PRO", layout="wide")
st.title("🔥 SKU Analyzer AI PRO (FINAL STABLE)")

threads = st.sidebar.slider("Threads", 1, 10, 5)
use_ai = st.sidebar.toggle("🤖 AI Mode")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])


# ---------------- SAFE URL DECODE ----------------
def decode_url(url):
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        if "page_link" in qs:
            return base64.b64decode(qs["page_link"][0]).decode("utf-8")

        return url
    except:
        return url


# ---------------- SAFE HTML FETCH (NO CRASH) ----------------
def get_html(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        r = requests.get(url, headers=headers, timeout=20)

        # block / redirect safe handling
        if r.status_code != 200:
            return ""

        return r.text

    except:
        return ""


# ---------------- SAFE NORMALIZE ----------------
def normalize(text):
    if text is None:
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


# ---------------- SAFE SELLER MATCH ----------------
def seller_match(html, sheet_seller):
    if not html:
        return False

    sheet = normalize(sheet_seller)
    html = html.lower()

    # simple keyword detection (robust)
    if sheet and sheet in html:
        return True

    return False


# ---------------- SAFE VERIFY ----------------
def verify(row):
    try:
        url = str(row.get("image_url", "") or "").strip()
        sku = str(row.get("product_sku", "") or "").strip()
        seller = str(row.get("product_seller", "") or "").strip()
        price_raw = row.get("product_price", 0)

        if not url:
            return row.name, "Missing URL", False, False, False

        real_url = decode_url(url)
        html = get_html(real_url)

        # ---------------- SAFE DEFAULTS ----------------
        if not html:
            return row.name, "Blocked/No HTML", False, False, False

        # ---------------- SKU ----------------
        try:
            sku_ok = ai_sku_match(html, sku) if use_ai else smart_sku_match(html, sku)
        except:
            sku_ok = False

        # ---------------- SELLER ----------------
        try:
            seller_ok = seller_match(html, seller)
        except:
            seller_ok = False

        # ---------------- PRICE ----------------
        try:
            price = clean_price(price_raw)
            price_ok = price_match_for_seller(html, seller, price)
        except:
            price_ok = False

        # ---------------- FINAL RESULT ----------------
        result = classify_result(sku_ok, seller_ok, price_ok)

        return row.name, result, sku_ok, seller_ok, price_ok

    except Exception:
        return row.name, "Error Safe Fallback", False, False, False


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

        # ---------------- UPDATE DF ----------------
        for idx, result, sku_ok, seller_ok, price_ok in results:
            df.loc[idx, "result"] = result
            df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
            df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
            df.loc[idx, "price_match"] = "Yes" if price_ok else "No"

        st.success("✅ DONE - NO ERRORS VERSION")

        # SAFE DISPLAY
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            "result.csv"
        )
