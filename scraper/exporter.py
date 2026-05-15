import os
import pandas as pd
from typing import List
from datetime import datetime
from loguru import logger
from .validator import BusinessLead

def export_data(leads: List[BusinessLead], query: str, location: str, format_type: str = "csv"):
    """
    Exports validated Pydantic models to CSV or XLSX format.
    Ensures outputs directory exists.
    """
    if not leads:
        logger.warning("No leads to export.")
        return

    os.makedirs("output", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = query.replace(" ", "_").lower()
    safe_loc = location.replace(" ", "_").replace(",", "").lower()
    
    base_filename = f"output/{safe_query}_{safe_loc}_{timestamp}"
    
    # Convert Pydantic objects to dicts
    data = [lead.model_dump() for lead in leads]
    df = pd.DataFrame(data)
    
    # Force timezone naive for excel serialization
    if 'scraped_at' in df.columns:
        df['scraped_at'] = df['scraped_at'].dt.tz_localize(None)

    if format_type.lower() == "csv":
        filepath = f"{base_filename}.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"Data exported successfully to {filepath}")
        
    elif format_type.lower() == "xlsx":
        filepath = f"{base_filename}.xlsx"
        
        metadata = pd.DataFrame([{
            "Query": query,
            "Location": location,
            "Total Records": len(leads),
            "Export Date": timestamp,
            "Tool": "Google Maps B2B Lead Scraper v1.0"
        }])
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
            
        logger.info(f"Data exported successfully to {filepath}")
    else:
        logger.error(f"Unsupported export format: {format_type}")

