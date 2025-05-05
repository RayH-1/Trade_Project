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

# Load image on demand (lazy loading)
@st.cache_data
def load_image(label):
    path = f"imports_app/plots/{label}.jpg"
    if os.path.exists(path):
        try:
            return Image.open(path).copy()  # avoid closed image error
        except Exception as e:
            print(f"Failed to load {label}: {e}")
            return None
    else:
        return None

# Initialize session state
if "playing" not in st.session_state:
    st.session_state.playing = False
if "frame_index" not in st.session_state:
    st.session_state.frame_index = 0
if "autoplay_timer" not in st.session_state:
    st.session_state.autoplay_timer = time.time()

# Page config
st.set_page_config(page_title="EU Trade Over Time", layout="centered")
st.title("📈 Change in Major Trading Partner Over Time")

month_labels = generate_month_labels()

# Controls
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Play"):
        st.session_state.playing = True
        st.session_state.autoplay_timer = time.time()  # Reset timer on play
with col2:
    if st.button("⏹️ Stop"):
        st.session_state.playing = False

# Slider (use separate key to avoid direct overwrite)
slider_val = st.slider("Select Date", 0, len(month_labels)-1, st.session_state.frame_index)
st.session_state.frame_index = slider_val  # Update index manually

# Show image and label
selected_label = month_labels[st.session_state.frame_index]
st.subheader(f"Date: {selected_label}")

# Load image on demand
img = load_image(selected_label)
if img:
    st.image(img, use_container_width=True)
else:
    st.warning("Image not found for selected date.")

# Auto-play logic
if st.session_state.playing:
    time_since_last_update = time.time() - st.session_state.autoplay_timer
    if time_since_last_update > 0.4:  # Update every 0.4 seconds
        st.session_state.frame_index = (st.session_state.frame_index + 1) % len(month_labels)
        st.session_state.autoplay_timer = time.time()  # Reset the timer to avoid speeding up
        # No manual rerun, Streamlit will automatically refresh when session_state changes
