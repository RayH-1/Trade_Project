import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import os

# Generate date labels
@st.cache_data
def generate_month_labels(start='2000-01', end=None):
    """
    Generate a list of month labels from start to end date in 'YYYY-MM' format.
    If end is not provided, it defaults to the current system month and year.
    
    Args:
        start (str): Starting month in 'YYYY-MM' format
        end (str, optional): Ending month in 'YYYY-MM' format. Defaults to current month/year.
    
    Returns:
        list: List of month labels in 'YYYY-MM' format
    """
    # If end is not provided, use current system date (month and year only)
    if end is None:
        now = datetime.now()
        end = now.strftime("%Y-%m")
    
    dates = []
    start_date = datetime.strptime(start, "%Y-%m")
    end_date = datetime.strptime(end, "%Y-%m")
    
    while start_date <= end_date:
        dates.append(start_date.strftime("%Y-%m"))
        start_date += timedelta(days=32)  # Add enough days to move to next month
        start_date = start_date.replace(day=1)  # Reset to 1st of the month
    
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
st.markdown("Data is from the IMF Direction of Trade. [Visit the GitHub for any specific image for Month-Year](https://github.com/RayH-1/Trade_Project/tree/main/imports_app/plots)")

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