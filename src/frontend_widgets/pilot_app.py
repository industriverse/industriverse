import streamlit as st
import pandas as pd
import requests
import json
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Industriverse Pilot Widget",
    page_icon="🏭",
    layout="wide"
)

# --- Sidebar ---
st.sidebar.title("Industriverse Pilot")
st.sidebar.markdown("**Area 12: Magnet Assembly**")
st.sidebar.caption("S-REAN Node: Active")

st.sidebar.markdown("---")
st.sidebar.info(f"Connected to: {API_BASE_URL}")

# --- Main Content ---
st.title(f"Sovereign Magnet Factory")

# S-REAN Header
col1, col2, col3, col4 = st.columns(4)
col1.metric("Sovereignty Score", "0.874", "+0.02")
col2.metric("Dy Reduction", "1.2% Target", "-0.4%")
col3.metric("Recycled Input", "145 Tons", "+12%")
col4.metric("Output Yield", "98.2%", "+0.5%")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Data Onboarding", "Microstructure Sim", "ASAL Proofs"])

with tab1:
    st.header("Furnace Telemetry Ingestion")
    uploaded_file = st.file_uploader("Upload Heat Treatment Logs (CSV)", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview:", df.head())
        if st.button("Ingest & Validate"):
            st.success("Data ingested! 4,200 records processed.")
            # In real app: POST to /capsules/{id}/ingest

    st.subheader("Live Sensors")
    st.metric(label="Furnace Temp (Zone 1)", value="1042 °C", delta="-2 °C")

with tab2:
    st.header("M2N2 Microstructure Evolution")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Optimization Parameters")
        grain_size = st.slider("Target Grain Size (nm)", 10, 100, 45)
        gbd_temp = st.slider("GBD Temperature (°C)", 800, 1000, 920)
        if st.button("Run Evolution"):
            st.info("Evolving microstructure...")
            # In real app: POST to /capsules/{id}/simulate
            st.success("Optimization complete! Coercivity increased by 4%.")
    
    with col2:
        st.subheader("Hysteresis Loop Prediction")
        # Mock chart
        chart_data = pd.DataFrame({
            'H (kOe)': range(-20, 21),
            'B (kG)': [x * 0.8 + (grain_size/100) for x in range(-20, 21)] # Dummy physics
        })
        st.line_chart(chart_data, x='H (kOe)', y='B (kG)')

with tab3:
    st.header("Sovereign Proof Bundle")
    st.markdown("### Verified Claims")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Performance Uplift", "Verified", "ASAL-SPA")
    col2.metric("Dy Content", "< 1.5%", "Compliance")
    col3.metric("Carbon Footprint", "Neutral", "Sustainability")
    
    st.markdown("---")
    st.markdown("**Proof Hash:** `0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069`")
    st.download_button("Download Certificate", "Simulated PDF Content", "proof.pdf")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Industriverse Sovereign Capsules | v1.0.0")
