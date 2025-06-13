import streamlit as st

st.title("📈 Analytics")

# Check if data exists in session state
if "returns" in st.session_state:
    df_returns = st.session_state["returns"]
    st.write("Returns Data:")
    st.dataframe(df_returns)
else:
    st.warning("Please upload Returns data first on the Upload page.")
