import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import os
import time

# Generate month labels
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

# Preload and cache all images
@st.cache_data
def preload_all_images():
    images = {}
    for label in generate_month_labels():
        path = f"imports_app/plots/{label}.jpg"
        if os.path.exists(path):
            try:
                images[label] = Image.open(path).copy()  # avoid closed image error
            except Exception as e:
                print(f"Failed to load {label}: {e}")
    return images

# Initialize session state
if "playing" not in st.session_state:
    st.session_state.playing = False
if "index" not in st.session_state:
    st.session_state.index = 0

# Setup app
st.set_page_config(page_title="European Union Trade (IMF)", layout="centered")
st.title("Change in Major Trading Partner Over Time")

# Generate labels and preload images
month_labels = generate_month_labels()
cached_images = preload_all_images()

# Play / Stop controls
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Play"):
        st.session_state.playing = True
with col2:
    if st.button("⏹️ Stop"):
        st.session_state.playing = False

# Slider to select index
st.session_state.index = st.slider(
    "Select Date",
    0, len(month_labels) - 1,
    value=st.session_state.index,
    key="slider"
)

# Display selected label
selected_label = month_labels[st.session_state.index]
st.subheader(f"Date: {selected_label}")

# Show image
img = cached_images.get(selected_label)
if img:
    st.image(img, use_container_width=True)
else:
    st.warning("Image not found for selected date.")

# Auto-play logic
if st.session_state.playing:
    time.sleep(0.4)  # Speed: lower is faster
    st.session_state.index = (st.session_state.index + 1) % len(month_labels)
    st.experimental_rerun()
