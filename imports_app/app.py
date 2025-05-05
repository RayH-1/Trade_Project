import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import os

# Generate date labels
@st.cache_data
def generate_month_labels(start='2000-01', end='2025-01'):
    dates = []
    start_date = datetime.strptime(start, "%Y-%m")
    end_date = datetime.strptime(end, "%Y-%m")
    while start_date <= datetime.strptime(end, "%Y-%m"):
        dates.append(start_date.strftime("%Y-%m"))
        start_date += timedelta(days=32)
        start_date = start_date.replace(day=1)
    return dates

# Load image
def load_image(label):
    path = f"imports_app/plots/{label}.png"
    if os.path.exists(path):
        return Image.open(path)
    else:
        return None

# Streamlit UI
st.set_page_config(page_title="Image Scroller", layout="centered")
st.title("📅 Image Timeline Viewer")

month_labels = generate_month_labels()

# Slider
index = st.slider("Select Date", 0, len(month_labels)-1, 0, format="%d")
selected_label = month_labels[index]
st.subheader(f"Date: {selected_label}")

# Show image
img = load_image(selected_label)
if img:
    st.image(img, use_column_width=True)
else:
    st.warning("Image not found for selected date.")
