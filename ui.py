import streamlit as st
import pandas as pd

def apply_custom_css():
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
        .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
        </style>
    """, unsafe_allow_html=True)

def render_stats(df):
    if "result" in df.columns:
        col1, col2, col3, col4 = st.columns(4)
        total = len(df)
        correct = len(df[df["result"] == "Correct"])
        col1.metric("Total Scanned", total)
        col2.metric("Verified OK", correct)
        col3.metric("Price Mismatch", len(df[df["result"] == "Price Wrong"]))
        col4.metric("Success Rate", f"{(correct/total)*100:.1f}%" if total > 0 else "0%")
