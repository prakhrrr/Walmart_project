import streamlit as st

st.set_page_config(
    page_title="Smart Product Return Portal",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Smart Product Return Portal")
st.markdown("""
Welcome to the smart product return portal. Use the sidebar to:
- Upload return/inventory/demand data
- Visualize and analyze returns
- Get optimal store rerouting suggestions
""")
