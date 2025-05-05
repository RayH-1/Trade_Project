import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from datetime import datetime, timedelta

# Generate month labels
def generate_month_labels(start='2000-01', end='2025-01'):
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
    try:
        img_path = f"imports_app/plots/{label}.png"
        img = Image.open(img_path)
        img = img.resize((800, 500), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading {label}: {e}")
        return None

# Slider callback
def on_slider_change(val):
    index = int(float(val))
    label = month_labels[index]
    img = load_image(label)
    if img:
        image_label.config(image=img)
        image_label.image = img
        title_var.set(label)
    else:
        title_var.set(f"{label} (not found)")

# Init window
app = ttk.Window(themename="darkly")  # Try "cosmo", "darkly", "flatly", etc.
app.title("Image Scroller")
app.geometry("900x650")

month_labels = generate_month_labels()
title_var = ttk.StringVar()

# Image display
image_label = ttk.Label(app)
image_label.pack(pady=10)

# Label
ttk.Label(app, textvariable=title_var, font=("Arial", 16)).pack()

# Styled slider
slider = ttk.Scale(app, from_=0, to=len(month_labels)-1, orient='horizontal',
                   command=on_slider_change, bootstyle="info", length=800)
slider.pack(pady=20)

# Load first image
on_slider_change(0)

app.mainloop()
