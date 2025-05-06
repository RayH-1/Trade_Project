import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import os
import time

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

# Set page config first, before any other Streamlit commands
st.set_page_config(page_title="EU Trade Over Time", layout="centered")

# Title and description
st.title("Change in Major Trading Partner Over Time")
st.markdown("Data is from the IMF Direction of Trade. [Visit the GitHub for any specific image for Month-Year](https://github.com/RayH-1/Trade_Project/tree/main/imports_app/plots)")

# Generate month labels
month_labels = generate_month_labels()

# Create columns for slider and play button
col1, col2 = st.columns([4, 1])

with col1:
    # Slider
    index = st.slider("Scroll to see changes over time", 0, len(month_labels)-1, 0, key="time_slider")
    selected_label = month_labels[index]

with col2:
    # Play/Pause button (unicode symbol in a circle)
    st.markdown("""
    <style>
    .play-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: #1E90FF;
        color: white;
        font-size: 24px;
        text-decoration: none;
        margin-top: 25px;
        cursor: pointer;
        border: none;
        transition: background-color 0.3s;
    }
    .play-button:hover {
        background-color: #0066CC;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for play/pause
    if 'playing' not in st.session_state:
        st.session_state.playing = False

    # Toggle play/pause function
    def toggle_play():
        st.session_state.playing = not st.session_state.playing

    # Button with play/pause symbol
    play_symbol = "⏸" if st.session_state.playing else "▶"
    play_button = st.button(play_symbol, key="play_button", help="Auto-scroll through time")
    
    if play_button:
        toggle_play()

st.subheader(f"Month-Year: {selected_label}")

# Show image
img = load_image(selected_label)
if img:
    st.image(img, use_container_width=True)
else:
    st.warning("Image not found for selected date.")

# Auto-scroll logic
if st.session_state.playing:
    if st.session_state.time_slider < len(month_labels) - 1:
        time.sleep(0.5)  # Control speed of auto-scroll
        st.session_state.time_slider += 1
        st.experimental_rerun()
    else:
        # Reset to beginning when reaching the end
        st.session_state.time_slider = 0
        st.experimental_rerun()