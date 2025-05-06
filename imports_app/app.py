import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import os
import re

@st.cache_data
def generate_month_labels(start='2000-01', end=None, plots_folder='plots/'):
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
        pattern = re.compile(r"\d{4}-\d{2}")
        months = []

        for name in os.listdir(plots_folder):
            match = pattern.match(name)
            if match:
                try:
                    months.append(datetime.strptime(match.group(), "%Y-%m"))
                except ValueError:
                    pass
        
        if months:
            end_date_obj = max(months)
            end = end_date_obj.strftime("%Y-%m")
        else:
            raise ValueError("No valid YYYY-MM date found in the plots folder.")

    # Generate date labels
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

# Streamlit UI
st.set_page_config(page_title="EU Trade Over Time", layout="centered")
st.title("Change in Major Trading Partner Over Time")

month_labels = generate_month_labels()

# Slider
index = st.slider("Scroll to see changes over time", 0, len(month_labels)-1, 0, format="%d")
selected_label = month_labels[index]
st.subheader(f"Month-Year: {selected_label}")

# Show image
img = load_image(selected_label)
if img:
    st.image(img, use_container_width=True)
else:
    st.warning("Image not found for selected date.")