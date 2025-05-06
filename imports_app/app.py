import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import os
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # Required for non-interactive environments

# Import our custom modules
from data_fetcher import fetch_imf_trade_data, fetch_area_codes, process_trade_data
from map_generator import load_geo_data, merge_data, generate_all_maps

# Generate date labels
@st.cache_data
def generate_month_labels(start='2000-01', end='2025-01'):
    dates = []
    start_date = datetime.strptime(start, "%Y-%m")
    end_date = datetime.strptime(end, "%Y-%m")
    while start_date <= end_date:
        dates.append(start_date.strftime("%Y-%m"))
        start_date += timedelta(days=32)
        start_date = start_date.replace(day=1)
    return dates

# Load image
def load_image(label):
    path = f"imports_app/plots/{label}.jpg"
    if os.path.exists(path):
        return Image.open(path)
    else:
        return None

# Data processing function with caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def process_data():
    # Create directories if they don't exist
    os.makedirs("imports_app/plots", exist_ok=True)
    
    with st.spinner("Fetching trade data from IMF..."):
        # Fetch trade data
        trade_data = fetch_imf_trade_data()
        
        # Fetch country codes
        area_codes = fetch_area_codes()
        code_dict = area_codes
        
        # Process trade data
        processed_data = process_trade_data(trade_data)
        
        # Load geographical data
        geo_data = load_geo_data('imports_app/geo/wab.geojson')
        
        # Merge data
        merged_data = merge_data(geo_data, processed_data, code_dict)
        
        # Generate all maps
        generate_all_maps(merged_data)
        
        return merged_data

# Streamlit UI
st.set_page_config(page_title="EU Trade Over Time", layout="centered")
st.title("📈 Change in Major Trading Partner Over Time")

# Add a button to refresh data
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# Process data
with st.spinner("Preparing visualization data..."):
    merged_data = process_data()

# Get available time periods
available_periods = sorted(merged_data['TIME_PERIOD'].dropna().unique())
month_labels = available_periods if available_periods else generate_month_labels()

# Slider
if month_labels:
    index = st.slider("Select Date", 0, len(month_labels)-1, 0, format="%d")
    selected_label = month_labels[index]
    st.subheader(f"Date: {selected_label}")

    # Show image
    img = load_image(selected_label)
    if img:
        st.image(img, use_container_width=True)
    else:
        st.warning("Image not found for selected date.")
else:
    st.error("No data available. Please check your data sources.")

# Add an info section
with st.expander("About this visualization"):
    st.markdown("""
    This visualization shows the major trading partners for countries around the world.
    
    **Color Code:**
    - 🔵 Blue: United States is the largest trading partner
    - 🔴 Red: China is the largest trading partner
    - 🟡 Yellow: European Union is the largest trading partner
    
    **Opacity:**
    The opacity of the color indicates the strength of the trading relationship:
    - Light shade: 0-25% share
    - Medium-light shade: 25-50% share
    - Medium-dark shade: 50-75% share
    - Dark shade: 75-100% share
    
    Data Source: IMF Direction of Trade Statistics (DOTS)
    """)