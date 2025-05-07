import streamlit as st
from PIL import Image
from datetime import datetime
import os

@st.cache_data
def generate_month_labels(start='2000-01', end=None, plots_folder='imports_app/plots/'):
    """Generate a list of month labels from start to end date in 'YYYY-MM' format."""
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

# Load image
def load_image(label):
    path = f"imports_app/plots/{label}.jpg"
    if os.path.exists(path):
        return Image.open(path)
    else:
        return None

# Basic page setup
st.set_page_config(page_title="EU Trade Over Time", layout="wide")

# Very minimal CSS - only essential adjustments
st.markdown("""
    <style>
    .block-container {padding-top: 1rem !important; padding-bottom: 0 !important;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Simple title
st.markdown("### Change in Major Trading Partner Over Time")

# Get month labels
month_labels = generate_month_labels()

# Slider in a single column for maximum width
index = st.slider("", 0, len(month_labels)-1, 0)
selected_label = month_labels[index]
st.markdown(f"**{selected_label}**")

# Load and display image - simple approach
img = load_image(selected_label)
if img:
    # Simple image display with automatic width calculation
    st.image(img, width=int(st.session_state.get("_screen_width", 1000) * 0.8))
else:
    st.warning("Image not found for selected date.")