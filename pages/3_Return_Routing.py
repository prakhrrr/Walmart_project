# Smart Product Return Routing - Beginner Friendly UI Version
import streamlit as st
import pandas as pd
import pydeck as pdk
from math import radians, sin, cos, sqrt, atan2
from sklearn.preprocessing import MinMaxScaler

# ---------- Haversine ----------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ---------- Caching CSVs ----------
@st.cache_data
def load_data():
    returns = pd.read_csv("returns.csv")
    inventory = pd.read_csv("store_inventory.csv")
    demand = pd.read_csv("store_demand.csv")
    return returns, inventory, demand

def main():
    st.set_page_config(page_title="Product Return Optimizer", layout="centered")
    st.title("📦 Product Return Optimizer")
    st.markdown("This tool helps e-commerce teams route returned products to the most optimal store location.")

    returns_df, inventory_df, demand_df = load_data()

    # Merge and fill NaNs
    inventory_df = pd.merge(inventory_df, demand_df, on=["store_id", "product_id"], how="left")
    inventory_df["past_week_sales"].fillna(0, inplace=True)

    # Sidebar Weights
    with st.sidebar:
        st.header("⚙️ Scoring Weights")
        stock_weight = st.slider("Stock (Lower is Better)", 0.0, 1.0, 0.5)
        sales_weight = st.slider("Sales (Higher is Better)", 0.0, 1.0, 0.3)
        distance_weight = st.slider("Distance (Closer is Better)", 0.0, 1.0, 0.2)

    # Normalize weights
    total = stock_weight + sales_weight + distance_weight
    stock_weight /= total
    sales_weight /= total
    distance_weight /= total

    use_boost = sum([stock_weight > 0, sales_weight > 0, distance_weight > 0]) > 1

    # Normalize inventory by product
    normalized = {}
    for product_id, group in inventory_df.groupby("product_id"):
        group = group.copy()
        group["stock_score"] = 1 - MinMaxScaler().fit_transform(group[["current_stock"]])
        group["sales_score"] = MinMaxScaler().fit_transform(group[["past_week_sales"]])
        normalized[product_id] = group

    # Recommendations
    results = []
    for _, row in returns_df.iterrows():
        pid = row["product_id"]
        r_lat, r_lng = row["return_location_lat"], row["return_location_lng"]

        if pid not in normalized:
            continue

        candidates = normalized[pid].copy()
        candidates["distance_km"] = candidates.apply(lambda x: haversine(r_lat, r_lng, x["lat"], x["lng"]), axis=1)
        candidates["distance_score"] = 1 - MinMaxScaler().fit_transform(candidates[["distance_km"]])
        boost = 0.5 * MinMaxScaler().fit_transform(candidates[["past_week_sales"]]) + 0.5 * (1 - MinMaxScaler().fit_transform(candidates[["distance_km"]]))
        candidates["boost"] = boost.flatten()

        candidates["score"] = (
            stock_weight * candidates["stock_score"] +
            sales_weight * candidates["sales_score"] +
            distance_weight * candidates["distance_score"]
        )
        if use_boost:
            candidates["score"] += 0.1 * candidates["boost"]

        top = candidates.loc[candidates["score"].idxmax()]
        results.append({
            "return_id": row["return_id"],
            "product_name": row["product_name"],
            "store_name": top["store_name"],
            "distance_km": round(top["distance_km"], 2),
            "score": round(top["score"], 3)
        })

    result_df = pd.DataFrame(results)

    # Filter options
    st.subheader("🔍 View Recommendations")
    selected = st.selectbox("Select a Return ID", result_df["return_id"] if not result_df.empty else [])
    if selected:
        entry = result_df[result_df["return_id"] == selected].iloc[0]
        st.write(f"**Product:** {entry['product_name']}")
        st.write(f"**Recommended Store:** {entry['store_name']}")
        st.write(f"**Distance:** {entry['distance_km']} km")
        st.write(f"**Score:** {entry['score']}")

    st.subheader("📊 Summary Table")
    st.dataframe(result_df)
    st.download_button("Download Recommendations", result_df.to_csv(index=False), "recommendations.csv")

if __name__ == "__main__":
    main()
