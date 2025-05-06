import streamlit as st
from datetime import datetime, timedelta
import os
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # Required for non-interactive environments
import requests
import xml.etree.ElementTree as ET

# Import our custom modules
from data_fetcher import fetch_imf_trade_data
from map_generator import load_geo_data, process_trade_data, merge_data, generate_map_image

# Set page configuration
st.set_page_config(page_title="EU Trade Over Time", layout="centered")
st.title("📈 Change in Major Trading Partner Over Time")

# Generate date labels for dropdown selection
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

# Get country code dictionary
@st.cache_data(ttl=3600)
def fetch_country_codes():
    url = "http://dataservices.imf.org/REST/SDMX_XML.svc/CodeList/CL_AREA_DOT"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"Failed to fetch country codes: {response.status_code}")
            return {}
            
        # Parse the XML response
        root = ET.fromstring(response.content)
        
        # Define namespace mapping
        namespaces = {
            'message': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message',
            'structure': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure'
        }
        
        # Extract codes and descriptions
        area_codes = {}
        for code in root.findall(".//structure:Code", namespaces):
            code_id = code.get("value")
            description = code.find("structure:Description", namespaces).text
            area_codes[code_id] = description
            
        return area_codes
    except Exception as e:
        st.error(f"Error fetching country codes: {str(e)}")
        return {}

# Initialize session state for data
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.merged_data = None
    st.session_state.current_image = None
    st.session_state.available_periods = []

# Function to load data on button press  
def load_data():
    with st.spinner("Fetching the latest trade data..."):
        try:
            # Get trade data
            trade_data = fetch_imf_trade_data()
            
            # Get country codes
            country_codes = fetch_country_codes()
            
            # Process the trade data
            processed_data = process_trade_data(trade_data)
            
            # Load geographical data
            geo_data = load_geo_data('imports_app/geo/wab.geojson')
            
            # Merge data
            merged_data = merge_data(geo_data, processed_data, country_codes)
            
            # Update session state
            st.session_state.merged_data = merged_data
            st.session_state.data_loaded = True
            st.session_state.available_periods = sorted(merged_data['TIME_PERIOD'].dropna().unique())
            
            # Default to the latest time period
            if st.session_state.available_periods:
                latest_period = st.session_state.available_periods[-1]
                st.session_state.selected_period = latest_period
                
                # Generate the map for the selected period
                st.session_state.current_image = generate_map_image(
                    merged_data, 
                    latest_period
                )
            
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False

# Fetch Data button
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("Fetch Latest Data"):
        load_data()

# Select date and display map
if st.session_state.data_loaded:
    # Show available time periods
    available_periods = st.session_state.available_periods
    
    # Create a dropdown for selecting time period
    selected_period = st.selectbox(
        "Select Time Period", 
        options=available_periods,
        index=len(available_periods)-1  # Default to most recent
    )
    
    # Update the map when selection changes
    if selected_period != st.session_state.get('selected_period'):
        st.session_state.selected_period = selected_period
        st.session_state.current_image = generate_map_image(
            st.session_state.merged_data, 
            selected_period
        )
    
    # Display map
    if st.session_state.current_image:
        st.image(st.session_state.current_image, use_container_width=True)
else:
    st.info("Click 'Fetch Latest Data' to load trade data and display visualization.")

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