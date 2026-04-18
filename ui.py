import streamlit as st
import plotly.express as px

def show_metrics(df):
    total = len(df)
    correct = (df["result"] == "Correct").sum()
    accuracy = round((correct / total) * 100, 2) if total else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Checked", total)
    col2.metric("Correct", correct)
    col3.metric("Accuracy %", accuracy)

def show_chart(df):
    fig = px.pie(df, names="result", title="Result Distribution")
    st.plotly_chart(fig, use_container_width=True)
