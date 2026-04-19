import streamlit as st
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper import fetch_content
from matcher import smart_sku_match, price_match_for_seller
from ui import apply_custom_css, render_stats
from db import save_to_history

st.set_page_config(page_title="PRO SKU ANALYZER", layout="wide")
apply_custom_css()

st.title("🛡️ SKU ULTRA PRO MAX")
st.subheader("Global Price & Seller Verification Dashboard")

uploaded_file = st.file_uploader("Upload target CSV (Columns: url, sku, seller, price)", type=["csv"])

def verify_process(row):
    try:
        url, sku, seller = str(row["url"]).strip(), str(row["sku"]), str(row["seller"])
        target_price = float(re.sub(r'[^0-9.]', '', str(row["price"])))

        html = fetch_content(url)
        if not html: return row.name, "Network Error", False, False, False

        sku_ok = smart_sku_match(html, sku)
        if not sku_ok: return row.name, "SKU Wrong", False, False, False

        seller_ok = seller.lower() in html.lower()
        if not seller_ok: return row.name, "Seller Not Found", True, False, False

        price_ok = price_match_for_seller(html, seller, target_price)
        if not price_ok: return row.name, "Price Wrong", True, True, False

        return row.name, "Correct", True, True, True
    except:
        return row.name, "Script Error", False, False, False

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if st.button("🔥 START DEEP ANALYSIS"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        table_placeholder = st.empty()
        
        results = []
        done = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(verify_process, row) for _, row in df.iterrows()]
            for future in as_completed(futures):
                idx, res, s_ok, sl_ok, p_ok = future.result()
                df.loc[idx, "result"] = res
                df.loc[idx, "sku_match"] = "✅" if s_ok else "❌"
                df.loc[idx, "seller_match"] = "✅" if sl_ok else "❌"
                df.loc[idx, "price_match"] = "✅" if p_ok else "❌"
                
                done += 1
                progress_bar.progress(done / len(df))
                status_text.text(f"Processing item {done} of {len(df)}...")
                table_placeholder.dataframe(df.head(done), use_container_width=True)

        st.divider()
        render_stats(df)
        save_to_history(df)
        
        st.download_button("📩 Download Verified Report", df.to_csv(index=False), "verified_data.csv", "text/csv")
