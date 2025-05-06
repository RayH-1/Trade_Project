import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
from matplotlib.legend_handler import HandlerBase
from matplotlib import font_manager
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import pandas as pd
import geopandas as gpd

# Custom handler for touching legend patches
class TouchingRectanglesHandler(HandlerBase):
    def __init__(self, alphas, **kw):
        HandlerBase.__init__(self, **kw)
        self.alphas = alphas
        self.num_segments = len(alphas)
        
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        rect_width = width / self.num_segments
        rects = []
        for i, alpha in enumerate(self.alphas):
            rect = plt.Rectangle(
                (xdescent + i * rect_width, ydescent), 
                rect_width, 
                height, 
                facecolor=orig_handle.get_facecolor(), 
                alpha=alpha,
                edgecolor='black', 
                linewidth=0.3,
                transform=trans
            )
            rects.append(rect)
        return rects

def load_geo_data(geo_path):
    """
    Load and clean geographical data
    """
    gdf = gpd.read_file(geo_path)
    
    # Drop columns we don't need
    columns_to_drop = ['iso3', 'status', 'color_code', 'french_short']
    gdf = gdf.drop(columns=columns_to_drop, errors='ignore')
    
    # Remove rows with missing ISO codes
    gdf.dropna(subset=['iso_3166_1_alpha_2_codes'], inplace=True)
    
    return gdf

def merge_data(gdf, trade_data, code_dict):
    """
    Merge trade data with geographical data and map codes to names
    """
    # Left join (keeps all rows from gdf and matches with data)
    merged = gdf.merge(
        trade_data,
        left_on='iso_3166_1_alpha_2_codes',
        right_on='Importer_Code',
        how='left'
    )
    
    # Map codes to country names
    merged['Highest_Exporter'] = merged['Highest_Source'].map(code_dict)
    
    return merged

def generate_map(merged_data, time_period, output_path):
    """
    Generate a map visualization for a specific time period
    """
    # Filter data for specific time period
    gdata = merged_data[merged_data['TIME_PERIOD'] == time_period].copy()
    
    # Define colors and alphas
    color_map = {
        'China': '#FF0000',  # Red
        'United States': '#0000FF',  # Blue
        'EU (Member States and Institutions of the European Union) changing composition': '#FFD700'  # Gold
    }
    alpha_map = {1: 0.3, 2: 0.5, 3: 0.7, 4: 1.0}
    
    # Assign colors and alphas
    gdata['color'] = gdata['Highest_Exporter'].map(color_map)
    gdata['alpha'] = gdata['bin'].map(alpha_map)

    # Create figure with Robinson projection
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson(central_longitude=10))
    
    # Set global view and add coastlines
    ax.set_global()
    ax.coastlines(linewidth=0.3)
    
    # Plot each combination of exporter and bin
    for exporter, color in color_map.items():
        for bin_num, alpha in alpha_map.items():
            subset = gdata[(gdata['Highest_Exporter'] == exporter) & (gdata['bin'] == bin_num)]
            if not subset.empty:
                subset.plot(
                    ax=ax, 
                    color=color, 
                    alpha=alpha, 
                    edgecolor='none',
                    transform=ccrs.PlateCarree()
                )

    # Custom legend with exporters
    exporter_info = {
        'EU': '#FFD700',
        'China': '#FF0000',
        'USA': '#0000FF'
    }
    alphas = [0.2, 0.5, 0.7, 1.0]
    
    legend_handles = []
    legend_labels = []
    handler_map = {}
    
    for name, color in exporter_info.items():
        # Create single patch per exporter
        handle = Patch(facecolor=color, edgecolor='black')
        legend_handles.append(handle)
        legend_labels.append(name)
        
        # Add custom handler for this patch
        handler_map[handle] = TouchingRectanglesHandler(alphas)

    # Create custom legend
    ax.legend(
        handles=legend_handles,
        labels=legend_labels,
        handler_map=handler_map,
        title="WHO IS THE LARGER TRADING PARTNER? (Percentage Share of the Three)",
        title_fontproperties=font_manager.FontProperties(weight='bold'),
        ncol=3,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        frameon=False,
        handlelength=8
    )

    # Title and cleanup
    ax.set_title(f"Top Import Source by Country ({time_period})", fontsize=14, fontweight='bold', pad=20)
    ax.axis('off')

    # Save figure
    plt.savefig(output_path, dpi=150)
    plt.close()

def generate_all_maps(merged_data, output_dir='imports_app/plots'):
    """
    Generate maps for all time periods in the data
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate maps for each time period if they don't already exist
    for time_period in merged_data['TIME_PERIOD'].dropna().unique():
        file_path = f'{output_dir}/{time_period}.jpg'
        if not os.path.exists(file_path):
            print(f"Generating map for {time_period}...")
            generate_map(merged_data, time_period, file_path)
        else:
            print(f"Map for {time_period} already exists, skipping...")