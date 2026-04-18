import os

project_name = "sku_checker_pro"

files = {
    "requirements.txt": """streamlit
pandas
requests
selenium
webdriver-manager
plotly
""",

    "matcher.py": """import re

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def smart_sku_match(html, sku):
    text = re.sub(r'<[^>]+>', ' ', html)
    text = normalize(text)
    sku_clean = normalize(sku)

    if sku_clean in text:
        return True

    parts = re.split(r'[-_\\s]+', sku.lower())
    parts = [normalize(p) for p in parts if len(p) >= 3]

    match_count = sum(1 for p in parts if p in text)
    return len(parts) > 0 and (match_count / len(parts)) >= 0.7

def smart_seller_match(html, seller):
    html = html.lower()
    parts = re.split(r'[\\W_]+', seller.lower())

    match_count = sum(1 for p in parts if len(p) >= 3 and p in html)
    return match_count >= max(1, len(parts)//2)

def clean_price(text):
    try:
        return round(float(re.sub(r'[^0-9.]', '', str(text))), 2)
    except:
        return 0.0

def price_match_for_seller(html, seller, target_price):
    html = html.lower()
    target_price = round(float(target_price), 2)

    prices = [round(float(p), 2) for p in re.findall(r'\\d+\\.?\\d*', html)]
    return target_price in prices
""",

    "scraper.py": """import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def fetch_requests(url):
    try:
        r = session.get(url, timeout=8)
        if r.status_code == 200:
            return r.text.lower()
    except:
        return ""
    return ""

def fetch_selenium(url):
    try:
        options = Options()
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url)
        time.sleep(5)

        html = driver.page_source.lower()
        driver.quit()

        return html
    except:
        return ""

def get_html(url):
    html = fetch_requests(url)
    if not html:
        html = fetch_selenium(url)
    return html
""",

    "utils.py": """def classify_result(sku_ok, seller_ok, price_ok):
    if not sku_ok:
        return "SKU Wrong"
    elif not seller_ok:
        return "Seller Wrong"
    elif not price_ok:
        return "Price Wrong"
    return "Correct"
""",

    "ui.py": """import streamlit as st
import plotly.express as px

def show_metrics(df):
    total = len(df)
    correct = (df["result"] == "Correct").sum()
    accuracy = round((correct / total) * 100, 2) if total else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Checked", total)
    col2.metric("Correct", correct)
    col3.metric("Accuracy %", accuracy)

def show_chart(df):
    fig = px.pie(df, names="result", title="Result Distribution")
    st.plotly_chart(fig, use_container_width=True)
""",

    "main.py": """import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import get_html
from matcher import smart_sku_match, smart_seller_match, clean_price, price_match_for_seller
from utils import classify_result
from ui import show_metrics, show_chart

st.set_page_config(page_title="SKU Analyzer PRO", layout="wide")
st.title("🔥 SKU Analyzer PRO")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

def verify(row):
    try:
        url = str(row["url"]).strip()
        html = get_html(url)

        if not html:
            return row.name, "Error", False, False, False

        sku_ok = smart_sku_match(html, row["sku"])
        seller_ok = smart_seller_match(html, row["seller"])
        price = clean_price(row["price"])
        price_ok = price_match_for_seller(html, row["seller"], price)

        result = classify_result(sku_ok, seller_ok, price_ok)

        return row.name, result, sku_ok, seller_ok, price_ok

    except:
        return row.name, "Error", False, False, False

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if st.button("🚀 Start Check"):
        progress = st.progress(0)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(verify, row) for _, row in df.iterrows()]

            for i, future in enumerate(as_completed(futures)):
                idx, result, sku_ok, seller_ok, price_ok = future.result()

                df.loc[idx, "result"] = result
                df.loc[idx, "sku_match"] = "Yes" if sku_ok else "No"
                df.loc[idx, "seller_match"] = "Yes" if seller_ok else "No"
                df.loc[idx, "price_match"] = "Yes" if price_ok else "No"

                progress.progress((i + 1) / len(df))

        st.success("✅ Completed")

        show_metrics(df)
        show_chart(df)

        st.dataframe(df)

        st.download_button(
            "📥 Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            "result.csv"
        )
"""
}

# Create project
os.makedirs(project_name, exist_ok=True)

for filename, content in files.items():
    with open(os.path.join(project_name, filename), "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Project created successfully!")
