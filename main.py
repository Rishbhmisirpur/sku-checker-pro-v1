import streamlit as st
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importing from your modular files
from scraper import fetch_content
from matcher import smart_sku_match, price_match_for_seller
from ui import apply_custom_css, render_stats
from db import save_to_history

# 1. Page Configuration
st.set_page_config(page_title="PRO SKU ANALYZER ULTRA", layout="wide")
apply_custom_css()

# 2. Header
st.title("🛡️ SKU ULTRA PRO MAX")
st.markdown("### Strict Seller & Price Verification Dashboard")
st.divider()

# 3. File Upload
uploaded_file = st.file_uploader("Upload CSV (Columns: url, sku, seller, price)", type=["csv"])

# 4. Processing Core Logic
def verify_process(row):
    """Processes a single row and returns fixed status keywords"""
    try:
        url = str(row["url"]).strip()
        sku = str(row["sku"])
        seller = str(row["seller"])
        # Clean price string to float
        target_price = float(re.sub(r'[^0-9.]', '', str(row["price"])))

        html = fetch_content(url)
        if not html: 
            return row.name, "Connection Error", False, False, False

        # SKU Matching Logic
        sku_ok = smart_sku_match(html, sku)
        if not sku_ok: 
            return row.name, "SKU Wrong", False, False, False

        # Seller Matching Logic
        seller_ok = seller.lower() in html.lower()
        if not seller_ok: 
            # Changed from 'Seller Missing' to 'Wrong Seller'
            return row.name, "Wrong Seller", True, False, False

        # Price Matching Logic
        price_ok = price_match_for_seller(html, seller, target_price)
        if not price_ok: 
            # Changed from 'Price Error' to 'Price Wrong'
            return row.name, "Price Wrong", True, True, False

        return row.name, "Correct", True, True, True

    except Exception as e:
        return row.name, f"Error: {str(e)}", False, False, False

# 5. Main Execution
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if st.button("🚀 START CLEAN ANALYSIS"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        table_placeholder = st.empty()
        
        done = 0
        total = len(df)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(verify_process, row) for _, row in df.iterrows()]
            
            for future in as_completed(futures):
                idx, status, s_ok, sl_ok, p_ok = future.result()
                
                # Update DataFrame for Dashboard
                df.loc[idx, "Status"] = status
                df.loc[idx, "sku_match"] = "✅" if s_ok else "❌"
                df.loc[idx, "seller_match"] = "✅" if sl_ok else "❌"
                df.loc[idx, "price_match"] = "✅" if p_ok else "❌"
                
                done += 1
                progress_bar.progress(done / total)
                status_text.text(f"Processed {done} / {total} items")
                table_placeholder.dataframe(df.iloc[:done], use_container_width=True)

        st.success("✅ Analysis Complete!")
        st.divider()
        
        # Stats Section (Using 'Status' column for results)
        df_stats = df.rename(columns={"Status": "result"})
        render_stats(df_stats)
        
        # 6. CLEAN DOWNLOAD LOGIC (Professional CSV)
        clean_df = df.copy()
        
        # Mapping Emojis to Yes/No for CSV
        mapping = {"✅": "Yes", "❌": "No"}
        clean_df["sku_match"] = clean_df["sku_match"].map(mapping)
        clean_df["seller_match"] = clean_df["seller_match"].map(mapping)
        clean_df["price_match"] = clean_df["price_match"].map(mapping)
        
        # We keep the 'Status' column in the CSV so you know WHY it failed
        csv_data = clean_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download Clean CSV (Yes/No)",
            data=csv_data,
            file_name="sku_verification_report.csv",
            mime="text/csv"
        )
        
        save_to_history(clean_df)
