import streamlit as st
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper import fetch_content
from matcher import smart_sku_match, price_match_for_seller, ai_deep_verify, smart_seller_match
from ui import apply_custom_css, render_stats
from db import save_to_history

st.set_page_config(page_title="SKU AI ANALYZER PRO", layout="wide")
apply_custom_css()

st.title("🛡️ SKU ULTRA PRO MAX + ARM AI")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

def verify_process(row):
    idx = row.name
    try:
        url = str(row["url"]).strip()
        sku = str(row["sku"])
        seller = str(row["seller"])
        price_str = re.sub(r'[^0-9.]', '', str(row["price"]))
        target_price = float(price_str) if price_str else 0.0

        html = fetch_content(url)
        
        if not html or len(html) < 500:
            # Re-try with AI directly if HTML is thin or network failed
            return idx, "Network Error/Blocked", False, False, False

        # 1. SKU Check
        sku_ok = smart_sku_match(html, sku)

        # 2. Seller Check (Using new smart match)
        seller_ok = smart_seller_match(html, seller)

        # 3. Price Check
        price_logic_ok = price_match_for_seller(html, seller, target_price)
        price_ok = price_logic_ok
        
        if not price_logic_ok or not seller_ok:
            # Double check with AI if logic fails
            price_ok = ai_deep_verify(html, sku, seller, target_price)
            if price_ok: # If AI says YES, we trust it for both seller and price
                seller_ok = True

        if sku_ok and seller_ok and price_ok:
            status_msg = "Correct"
        else:
            errors = []
            if not sku_ok: errors.append("SKU Wrong")
            if not seller_ok: errors.append("Seller Wrong")
            if not price_ok: errors.append("Price Wrong")
            status_msg = " | ".join(errors)

        return idx, status_msg, sku_ok, seller_ok, price_ok

    except Exception as e:
        return idx, f"Error: {str(e)}", False, False, False

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if st.button("🔥 START AI ANALYSIS"):
        progress = st.progress(0)
        table_area = st.empty()
        done = 0
        df["Status"] = "Pending"
        
        # Reduced workers to 3 to prevent rapid blocking/network errors
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(verify_process, row) for _, row in df.iterrows()]
            for future in as_completed(futures):
                idx, status, s_ok, sl_ok, p_ok = future.result()
                df.at[idx, "Status"] = status
                df.at[idx, "sku_match"] = "✅" if s_ok else "❌"
                df.at[idx, "seller_match"] = "✅" if sl_ok else "❌"
                df.at[idx, "price_match"] = "✅" if p_ok else "❌"
                done += 1
                progress.progress(done / len(df))
                table_area.dataframe(df, use_container_width=True)

        st.success("Analysis Finished!")
        render_stats(df.rename(columns={"Status": "result"}))
        st.download_button("📥 Download Results", df.to_csv(index=False), "results.csv", "text/csv")
