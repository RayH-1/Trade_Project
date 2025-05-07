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
        
        width, height = img.size

        crop_side = int(width * 0.12)
        crop_top = int(height * 0.10)
        # Crop box: (left, upper, right, lower)
        cropped_img = img.crop((crop_side, crop_top, width - crop_side, height))
        
        return cropped_img
    else:
        return None

# Streamlit UI
st.set_page_config(page_title="EU Trade Over Time", layout="wide")  # Set to wide layout

# Use custom CSS to ensure consistent text sizes
st.markdown("""
    <style>
        /* Light theme settings */
    html, body, [class*="st-"] {
        color: #262730;
        background-color: #ffffff;
    }
                    
    .title {
        font-size: 1.1rem !important;
        font-weight: bold;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .subtitle {
        font-size: 1rem !important;
        margin-bottom: 1rem;
        text-align: center;
    }
    .stSlider, .stSlider > label {
        font-size: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS classes
st.markdown('<div class="title">Change in Major Trading Partner Over Time</div>', unsafe_allow_html=True)

# Create container for better spacing
main_container = st.container()

with main_container:
    month_labels = generate_month_labels()
    
    # Slider with improved styling
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        index = st.slider(
            "Scroll to see changes over time", 
            0, 
            len(month_labels)-1, 
            0, 
            format="%d"
        )
    
    selected_label = month_labels[index]
    st.markdown(f'<div class="subtitle">Month-Year: {selected_label}</div>', unsafe_allow_html=True)
    
    # Show image with minimal padding
    img = load_image(selected_label)
    if img:
        # Create columns to center the image better
        col1, col2, col3 = st.columns([1.5, 5, 1.5])
        with col2:
            st.image(img, use_container_width=True)
    else:
        st.warning("Image not found for selected date.")