import streamlit as st
import pandas as pd

st.title("📤 Upload CSV Files")

# Upload and save to session state
returns_file = st.file_uploader("Upload Returns CSV", type=["csv"])
if returns_file:
    df_returns = pd.read_csv(returns_file)
    st.session_state["returns"] = df_returns
    st.write("Returns Data Preview:")
    st.dataframe(df_returns)

inventory_file = st.file_uploader("Upload Inventory CSV", type=["csv"])
if inventory_file:
    df_inventory = pd.read_csv(inventory_file)
    st.session_state["inventory"] = df_inventory
    st.write("Inventory Data Preview:")
    st.dataframe(df_inventory)

demand_file = st.file_uploader("Upload Demand CSV", type=["csv"])
if demand_file:
    df_demand = pd.read_csv(demand_file)
    st.session_state["demand"] = df_demand
    st.write("Demand Data Preview:")
    st.dataframe(df_demand)
