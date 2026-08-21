import streamlit as st

st.set_page_config(page_title="Wishlist Discovery Engine", layout="wide")

st.title("Wishlist Discovery Engine")
st.caption("Why do people save fashion items but not buy them?")

tab1, tab2, tab3, tab4 = st.tabs(["Findings", "Evidence", "Live analysis", "How it works"])

with tab1:
    st.info("Charts coming soon.")

with tab2:
    st.info("Quotes and sources coming soon.")

with tab3:
    st.info("Live classifier coming soon.")

with tab4:
    st.info("Method and validation coming soon.")

st.divider()
st.caption("Concept prototype. Not affiliated with Myntra.")