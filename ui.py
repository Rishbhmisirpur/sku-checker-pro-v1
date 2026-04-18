import streamlit as st

# 🔥 SaaS THEME
def apply_theme():
    st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
            color: white;
        }

        .stButton>button {
            border-radius: 8px;
            height: 3em;
            background-color: #ff4b4b;
            color: white;
            font-weight: bold;
        }

        .stDataFrame {
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)


# 📊 METRICS
def show_metrics(df):
    total = len(df)
    matched = len(df[df["result"] == "Match"])
    failed = len(df[df["result"] != "Match"])
    acc = (matched / total * 100) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", total)
    col2.metric("Matched", matched)
    col3.metric("Failed", failed)
    col4.metric("Accuracy", f"{acc:.2f}%")

    st.markdown("---")


# 📈 CHART
def show_chart(df):
    st.subheader("📊 Result Summary")

    if "result" in df.columns:
        st.bar_chart(df["result"].value_counts())
    else:
        st.info("No result data available")
