import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import os
import numpy as np

@st.cache_data
def generate_month_labels(start='2000-01', end=None, plots_folder='imports_app/plots/'):
    """
    Generate a list of month labels from start to end date in 'YYYY-MM' format.
    If end is not provided, it defaults to the latest YYYY-MM found in the plots folder.
    
    Args:
        start (str): Starting month in 'YYYY-MM' format
        end (str, optional): Ending month in 'YYYY-MM' format or determined from folder content.
        plots_folder (str): Path to the folder where month data is stored.
    
    Returns:
        list: List of month labels in 'YYYY-MM' format
    """
    # Get latest date from plots folder if end is not provided
    if end is None:
        months = []
        
        for filename in os.listdir(plots_folder):
            if filename.endswith('.jpg'):
                date_str = filename[:-4]  # remove '.jpg'
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m")
                    months.append(date_obj)
                except ValueError:
                    continue
        
        if months:
            end = max(months).strftime("%Y-%m")
        else:
            raise ValueError("No valid YYYY-MM date found in the plots folder.")

    # Generate date labels
    dates = []
    current_date = datetime.strptime(start, "%Y-%m")
    end_date = datetime.strptime(end, "%Y-%m")
    
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m"))
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return dates

# Load and crop image to remove excess white space
def load_image(label):
    path = f"imports_app/plots/{label}.jpg"
    if os.path.exists(path):
        img = Image.open(path)
        
        # Crop some of the left and right sides to focus on the map
        width, height = img.size
        crop_amount = int(width * 0.12)  # Crop 12% from each side
        cropped_img = img.crop((crop_amount, 0, width - crop_amount, height))
        
        return cropped_img
    else:
        return None

# Streamlit UI - Set light theme and wide layout
st.set_page_config(
    page_title="EU Trade Over Time", 
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🇪🇺",
    menu_items=None
)

# Use custom CSS to ensure consistent text sizes, light theme, and compact layout
st.markdown("""
    <style>
    /* Light theme settings */
    html, body, [class*="st-"] {
        color: #262730;
        background-color: #ffffff;
    }
    
    /* Force ultra-compact layout with no margins */
    .stApp {
        margin: 0;
        padding: 0;
    }
    
    /* Remove padding around elements completely */
    .element-container, .stMarkdown, section {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    .title {
        font-size: 1.8rem !important;
        font-weight: bold;
        margin: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0.3rem !important;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.4rem !important;
        margin: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0.3rem !important;
        text-align: center;
    }
    
    /* Make slider ultra-compact */
    .stSlider {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stSlider > label {
        font-size: 1.1rem !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Hide fullscreen button on images to save space */
    button[title="View fullscreen"] {
        display: none;
    }
    
    /* Remove default streamlit margins completely */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide hamburger menu */
    header {
        visibility: hidden;
    }
    
    /* Hide footer */
    footer {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# Create a very compact layout
st.markdown('<div class="title">Change in Major Trading Partner Over Time</div>', unsafe_allow_html=True)

# Generate month labels
month_labels = generate_month_labels()

# Slider with no column layout to save space
index = st.slider(
    "Scroll to see changes over time", 
    0, 
    len(month_labels)-1, 
    0, 
    format="%d",
    key="time_slider"
)

selected_label = month_labels[index]
st.markdown(f'<div class="subtitle">Month-Year: {selected_label}</div>', unsafe_allow_html=True)

# Show image with slight margin to ensure no scrolling
img = load_image(selected_label)
if img:
    # Display image using container width without column layout
    st.image(img, use_container_width=True)
else:
    st.warning("Image not found for selected date.")