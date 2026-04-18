import streamlit as st

def chat_support():
    st.sidebar.title("💬 Support Chat")

    msg = st.sidebar.text_input("Ask issue")

    if st.sidebar.button("Send"):
        st.sidebar.success("Support: We received your query. We will fix it soon.")


def show_metrics(df):
    st.subheader("📊 Summary")
    st.write(df["result"].value_counts())


def show_chart(df):
    st.bar_chart(df["result"].value_counts())
