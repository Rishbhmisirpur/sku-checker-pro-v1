import streamlit as st
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper import fetch_content
from matcher import smart_sku_match, price_match_for_seller, ai_verify

st.set_page_config(page_title="SKU AI ANALYZER PRO", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00ffcc; }
    .stButton>button { background: linear-gradient(45deg, #ff4b4b, #ff8181); color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ SKU ULTRA PRO MAX (AI Enabled)")
st.subheader("Global Price & Seller Verification Engine")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

def process_row(row):
    try:
        url, sku, seller = str(row["url"]).strip(), str(row["sku"]), str(row["seller"])
        price = float(re.sub(r'[^0-9.]', '', str(row["price"])))

        html = fetch_content(url)
        if not html: return row.name, "Network Error", "❌", "❌", "❌"

        # Using your exact logic
        sku_ok = smart_sku_match(html, sku)
        if not sku_ok: return row.name, "SKU Mismatch", "❌", "❌", "❌"

        seller_ok = seller.lower() in html.lower()
        if not seller_ok: return row.name, "Seller Missing", "✅", "❌", "❌"

        price_ok = price_match_for_seller(html, seller, price)
        if not price_ok: return row.name, "Price Error", "✅", "✅", "❌"

        return row.name, "Verified", "✅", "✅", "✅"
    except:
        return row.name, "System Error", "❌", "❌", "❌"

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if st.button("🔥 START DEEP SCAN"):
        bar = st.progress(0)
        table = st.empty()
        
        for i, row in df.iterrows():
            idx, status, s, sl, p = process_row(row)
            df.loc[idx, "Status"] = status
            df.loc[idx, "SKU_Match"] = s
            df.loc[idx, "Seller_Match"] = sl
            df.loc[idx, "Price_Match"] = p
            
            bar.progress((i + 1) / len(df))
            table.dataframe(df.head(i+1), use_container_width=True)

        # Dashboard Metrics
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Items", len(df))
        c2.metric("Verified OK", len(df[df["Status"] == "Verified"]))
        c3.metric("Errors Found", len(df[df["Status"] != "Verified"]))

        # --- CLEAN DOWNLOAD (NO EXTRA KEYWORDS) ---
        clean_df = df.copy()
        emoji_map = {"✅": "Yes", "❌": "No"}
        clean_df["SKU_Match"] = clean_df["SKU_Match"].map(emoji_map)
        clean_df["Seller_Match"] = clean_df["Seller_Match"].map(emoji_map)
        clean_df["Price_Match"] = clean_df["Price_Match"].map(emoji_map)
        
        st.download_button(
            "📩 Download Professional Report",
            clean_df.to_csv(index=False).encode('utf-8'),
            "verified_report.csv",
            "text/csv"
        )
