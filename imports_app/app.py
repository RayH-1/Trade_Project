import streamlit as st
from PIL import Image
from datetime import datetime
import os

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
        
        # Crop more aggressively to fit in viewport
        width, height = img.size
        crop_left = int(width * 0.15)  # Crop 15% from each side
        crop_right = int(width * 0.15)
        crop_top = int(height * 0.05)   # Crop 5% from top and bottom
        crop_bottom = int(height * 0.05)
        
        cropped_img = img.crop((crop_left, crop_top, width - crop_right, height - crop_bottom))
        
        return cropped_img
    else:
        return None

# Streamlit UI
st.set_page_config(
    page_title="EU Trade Over Time", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapse sidebar by default to maximize space
)

# Use custom CSS to ensure viewport fit
st.markdown("""
    <style>
        /* Fix viewport height */
        html, body, [class*="css"] {
            height: 100vh !important;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        
        /* Remove unnecessary padding */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            max-width: 100% !important;
        }
        
        /* Reduce spacing */
        .stSlider [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }
        
        /* Compact title */
        .title {
            font-size: 1.5rem !important;
            font-weight: bold;
            margin-bottom: 0rem;
            text-align: center;
            padding: 0;
        }
        
        /* Smaller subtitle */
        .subtitle {
            font-size: 1rem !important;
            margin-bottom: 0rem;
            text-align: center;
        }
        
        /* Compact slider */
        .stSlider {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Make image container fit viewport */
        .stImage > img {
            max-height: calc(100vh - 120px) !important;
            width: auto !important;
            object-fit: contain;
        }
    </style>
    """, unsafe_allow_html=True)

# Create a more compact layout
st.markdown('<div class="title">Change in Major Trading Partner Over Time</div>', unsafe_allow_html=True)

month_labels = generate_month_labels()

# Create a more compact slider
col1, col2, col3 = st.columns([1, 10, 1])
with col2:
    index = st.slider(
        "", # Remove label for space savings
        0, 
        len(month_labels)-1, 
        0,
        format="%d"
    )

selected_label = month_labels[index]
st.markdown(f'<div class="subtitle">Month-Year: {selected_label}</div>', unsafe_allow_html=True)

# Display image optimized for viewport
img = load_image(selected_label)
if img:
    # Use a container to maintain aspect ratio while filling available space
    image_container = st.container()
    with image_container:
        st.image(img, use_column_width=True)
else:
    st.warning("Image not found for selected date.")