import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import base64
import requests
import random
import time
from urllib.parse import urlparse, parse_qs

from matcher import smart_sku_match, ai_sku_match, clean_price, price_match_for_seller
from utils import classify_result


# ---------------- SESSION (IMPORTANT) ----------------
session = requests.Session()


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
st.title("🔥 SKU Analyzer AI PRO (NEXT LEVEL ENGINE)")

threads = st.sidebar.slider("Threads", 1, 10, 5)
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


# ---------------- ULTRA FETCH ENGINE ----------------
def get_html(url):
    try:
        headers_pool = [
            {"User-Agent": "Mozilla/5.0 Chrome/124"},
            {"User-Agent": "Mozilla/5.0 Firefox/120"},
            {"User-Agent": "Mozilla/5.0 Safari/537"},
            {"User-Agent": "Mozilla/5.0 Windows NT 10.0"},
        ]

        for _ in range(4):
            headers = random.choice(headers_pool)

            r = session.get(
                url,
                headers=headers,
                timeout=25,
                allow_redirects=True
            )

            html = r.text or ""

            # 🔥 IMPORTANT: accept partial HTML also
            if len(html) > 150:
                return html

            time.sleep(1)

        return ""

    except:
        return ""


# ---------------- CLEAN ----------------
def clean(text):
    if not text:
        return ""
    return str(text).lower().strip()


# ---------------- SMART MATCH ENGINE ----------------
def smart_match(html, value):
    if not html or not value:
        return False

    html = html.lower()
    value = clean(value)

    # direct match
    if value in html:
        return True

    # token match
    v_tokens = set(value.split())
    h_tokens = set(re.findall(r"[a-z0-9]+", html))

    if len(v_tokens & h_tokens) >= max(1, len(v_tokens)//2):
        return True

    return False


# ---------------- VERIFY ----------------
def verify(row):
    try:
        url = str(row.get("image_url", "") or "").strip()
        sku = str(row.get("product_sku", "") or "").strip()
        seller = str(row.get("product_seller", "") or "").strip()
        price_raw = row.get("product_price", "")

        if not url:
            return row.name, "Missing URL", False, False, False

        real_url = decode_url(url)
        html = get_html(real_url)

        # 🔥 NEXT LEVEL FIX (NO FALSE BLOCK)
        if not html:
            return row.name, "No HTML (fallback processed)", False, False, False

        # ---------------- SKU ----------------
        try:
            sku_ok = smart_match(html, sku)
        except:
            sku_ok = False

        # ---------------- SELLER ----------------
        try:
            seller_ok = smart_match(html, seller)
        except:
            seller_ok = False

        # ---------------- PRICE ----------------
        try:
            price = clean(price_raw)
            price_ok = smart_match(html, price)
        except:
            price_ok = False

        result = classify_result(sku_ok, seller_ok, price_ok)

        return row.name, result, sku_ok, seller_ok, price_ok

    except Exception:
        return row.name, "Safe Error", False, False, False


# ---------------- MAIN ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Preview")
    st.dataframe(df.head())

    if st.button("🚀 RUN NEXT LEVEL ENGINE"):

        progress = st.progress(0)
        results = []

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(verify, row) for _, row in df.iterrows()]

            for i, f in enumerate(as_completed(futures)):
                results.append(f.result())
                progress.progress((i + 1) / len(df))

        # ---------------- UPDATE ----------------
        for idx, result, sku_ok, seller_ok, price_ok in results:
            df.loc[idx, "result"] = result
            df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
            df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
            df.loc[idx, "price_match"] = "Yes" if price_ok else "No"

        st.success("🔥 NEXT LEVEL ENGINE COMPLETE")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False),
            "result.csv"
        )
