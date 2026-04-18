import streamlit as st
import pandas as pd


# ---------------- CHAT SUPPORT ----------------
def chat_support():
    st.sidebar.title("💬 Support Chat")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    msg = st.sidebar.text_input("Ask your issue")

    if st.sidebar.button("Send"):
        if msg:
            st.session_state.chat.append(("User", msg))
            st.session_state.chat.append(("Bot", "We received your request. Team will review it."))

    for sender, text in st.session_state.chat[-6:]:
        st.sidebar.write(f"**{sender}:** {text}")


# ---------------- METRICS ----------------
def show_metrics(df):
    st.subheader("📊 Result Summary")

    if "result" in df.columns:
        st.write(df["result"].value_counts())
    else:
        st.warning("No result column found")


# ---------------- CHART ----------------
def show_chart(df):
    if "result" in df.columns:
        st.bar_chart(df["result"].value_counts())
