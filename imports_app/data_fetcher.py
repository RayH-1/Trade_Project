import sdmx
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import os

def fetch_imf_trade_data():
    """
    Fetch trade data from IMF's Direction of Trade Statistics (DOTS)
    Returns processed DataFrame with trade values
    """
    client = sdmx.Client()
    url = (
        "http://dataservices.imf.org/REST/SDMX_XML.svc/CompactData/"
        "DOT/M..TMG_CIF_USD.US+CN+B0"
        "?startPeriod=2000&format=sdmx-2.1"
    )
    
    # Retrieve SDMX data message
    message = client.get(url=url)
    
    # Convert to pandas Series with multi-index
    df = sdmx.to_pandas(message.data[0])
    
    # Convert to DataFrame and reset index
    df_flat = df.reset_index()
    
    # Pivot to wide format
    df_wide = df_flat.pivot_table(
        index=['REF_AREA', 'TIME_PERIOD'],
        columns='COUNTERPART_AREA',
        values='value',
        aggfunc='first'
    )
    
    # Reset column names and index
    df_wide.reset_index(inplace=True)
    df_wide.columns.name = None
    
    # Rename columns for clarity
    data = df_wide.rename(columns={
        'FREQ': 'Data Granularity',
        'REF_AREA': 'Importer_Code',
        'INDICATOR': 'Indicator',
        'COUNTERPART_AREA': 'Exporter_Code',
    })
    
    return data

def fetch_area_codes():
    """
    Fetch country/area codes and descriptions from IMF
    Returns a dictionary mapping codes to descriptions
    """
    url = "http://dataservices.imf.org/REST/SDMX_XML.svc/CodeList/CL_AREA_DOT"
    response = requests.get(url)
    
    # Parse XML response
    root = ET.fromstring(response.content)
    
    # Define namespace mapping
    namespaces = {
        'message': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message',
        'structure': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/structure'
    }
    
    # Extract codes and descriptions
    area_codes = {}
    for code in root.findall(".//structure:Code", namespaces):
        code_id = code.get("value")
        description = code.find("structure:Description", namespaces).text
        area_codes[code_id] = description
    
    return area_codes

def process_trade_data(data):
    """
    Process trade data to find highest trading partner for each country
    """
    def get_highest_source(row):
        # Handle potential NaN values
        b0 = row.get('B0', 0) or 0
        cn = row.get('CN', 0) or 0
        us = row.get('US', 0) or 0
        
        total = b0 + cn + us
        if total == 0:
            return 'Unknown', 0
            
        max_value = max(b0, cn, us)
        if max_value == b0:
            return 'B0', max_value / total
        elif max_value == cn:
            return 'CN', max_value / total
        else:
            return 'US', max_value / total
    
    # Apply function to create new columns
    data[['Highest_Source', 'Max_Share']] = data.apply(
        lambda row: pd.Series(get_highest_source(row)), axis=1
    )
    
    # Create binned categories based on Max_Share
    data['bin'] = data['Max_Share'].apply(lambda value: 
        1 if value <= 0.25 else
        2 if value <= 0.5 else
        3 if value <= 0.75 else
        4
    )
    
    return data