import streamlit as st
import pandas as pd
import re
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper import fetch_content
from matcher import smart_sku_match, price_match_for_seller, ai_deep_verify, smart_seller_match
from ui import apply_custom_css, render_stats
from db import save_to_history

st.set_page_config(page_title="SKU AI ANALYZER PRO", layout="wide")
apply_custom_css()

st.title("🛡️ SKU ULTRA PRO MAX + ARM AI")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])


def get_value(row, possible_cols):
    for col in possible_cols:
        if col in row.index:
            return row[col]
    return ""


def verify_process(row):
    idx = row.name

    try:
        url = str(get_value(row, ["url", "image_url", "pdp_url"])).strip()
        sku = str(get_value(row, ["sku", "product_sku"])).strip()
        seller = str(get_value(row, ["seller", "product_seller"])).strip()
        price_value = get_value(row, ["price", "product_price"])

        price_str = re.sub(r'[^0-9.]', '', str(price_value))
        target_price = float(price_str) if price_str else 0.0

        if not url:
            return idx, "URL Missing", False, False, False

        html = fetch_content(url)

        if not html or len(html) < 500:
            return idx, "Network Error/Blocked", False, False, False

        sku_ok = smart_sku_match(html, sku)
        seller_ok = smart_seller_match(html, seller)

        # Price logic same rakha hai
        price_logic_ok = price_match_for_seller(html, seller, target_price)
        price_ok = price_logic_ok

        if not price_logic_ok or not seller_ok:
            price_ok = ai_deep_verify(html, sku, seller, target_price)
            if price_ok:
                seller_ok = True

        if sku_ok and seller_ok and price_ok:
            status_msg = "Correct"
        else:
            errors = []
            if not sku_ok:
                errors.append("SKU Wrong")
            if not seller_ok:
                errors.append("Seller Wrong")
            if not price_ok:
                errors.append("Price Wrong")
            status_msg = " | ".join(errors)

        return idx, status_msg, sku_ok, seller_ok, price_ok

    except Exception as e:
        return idx, f"Error: {str(e)}", False, False, False


if uploaded_file:
    try:
        file_bytes = uploaded_file.getvalue()
        df = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8-sig')
    except Exception:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding='latin-1')
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
            st.stop()

    if st.button("🔥 START AI ANALYSIS"):
        progress = st.progress(0)
        table_area = st.empty()
        done = 0

        df["Status"] = "Pending"
        df["sku_match"] = ""
        df["seller_match"] = ""
        df["price_match"] = ""

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

        try:
            render_stats(df.rename(columns={"Status": "result"}))
        except Exception:
            pass

        try:
            save_to_history(df)
        except Exception:
            pass

        clean_df = df.copy()
        mapping = {"✅": "Yes", "❌": "No"}

        for col in ["sku_match", "seller_match", "price_match"]:
            if col in clean_df.columns:
                clean_df[col] = clean_df[col].replace(mapping)

        csv_output = clean_df.to_csv(index=False, encoding='utf-8-sig')

        st.download_button(
            label="📥 Download Clean CSV",
            data=csv_output,
            file_name="ai_analysis_results.csv",
            mime="text/csv"
        )
