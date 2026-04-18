import streamlit as st

def render_row(df):
    placeholder = st.empty()

    latest = df.dropna(subset=["result"]).tail(5)

    with placeholder.container():
        for _, r in latest.iterrows():
            st.markdown("---")
            c1, c2 = st.columns([1, 2])

            with c1:
                st.write("SKU:", r["sku"])
                st.write("Seller:", r["seller"])
                st.write("Price:", r["price"])
                st.write("Result:", r["result"])

            with c2:
                st.markdown(
                    f'<iframe src="{r["url"]}" width="100%" height="300"></iframe>',
                    unsafe_allow_html=True
                )


def render_result(df):
    st.success("✅ Completed")

    st.download_button(
        "📥 Download",
        df.to_csv(index=False).encode(),
        "result.csv"
    )
