import streamlit as st


def chat_support():
    st.sidebar.title("💬 Support")

    msg = st.sidebar.text_input("Ask issue")

    if st.sidebar.button("Send"):
        st.sidebar.success("Request received")


def show_metrics(df):
    st.subheader("📊 Summary")

    if "final_result" in df.columns:
        st.write(df["final_result"].value_counts())

    if "sku_match" in df.columns:
        st.write(df["sku_match"].value_counts())

    if "seller_match" in df.columns:
        st.write(df["seller_match"].value_counts())

    if "price_match" in df.columns:
        st.write(df["price_match"].value_counts())


def show_chart(df):
    if "final_result" in df.columns:
        st.bar_chart(df["final_result"].value_counts())
