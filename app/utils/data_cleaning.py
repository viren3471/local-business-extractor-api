import pandas as pd
import re

def clean_business_data(raw_data: list) -> pd.DataFrame:
    """Cleans the raw API data and normalizes string values."""
    if not raw_data:
        return pd.DataFrame()
        
    df = pd.DataFrame(raw_data)
    
    # 1. Deduplication using Source Record ID
    df = df.drop_duplicates(subset=["Source Record ID"])
    
    # 2. Clean whitespace
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # 3. Normalize categories
    df["Business Category"] = df["Business Category"].str.title()
    
    # 4. Handle missing values
    df.fillna("Not Available", inplace=True)
    
    # 5. Validate Phone Numbers (Keep structural characters, strip junk)
    def clean_phone(phone):
        if phone == "Not Available":
            return phone
        # Keep digits, spaces, plus, and parentheses
        cleaned = re.sub(r'[^\d\+\-\s\(\)]', '', str(phone)).strip()
        return cleaned if cleaned else "Not Available"
        
    df["Phone Number"] = df["Phone Number"].apply(clean_phone)
    
    return df

def generate_analytics(df: pd.DataFrame, total_api_records: int) -> dict:
    """Generates statistics distinguishing total vs unique and verified records."""
    if df.empty:
        return {
            "Total API Records": total_api_records,
            "Unique Businesses": 0
        }
        
    # Analyze Opening Hours
    all_times = []
    sunday_open = 0
    
    for hours in df["Opening Hours"]:
        if hours != "Not Available":
            # Extract times matching HH:MM using regex
            times = re.findall(r'\b([0-1]?[0-9]|2[0-3]):([0-5][0-9])\b', str(hours))
            for h, m in times:
                all_times.append(f"{h.zfill(2)}:{m}")
            
            # Basic OpenStreetMap logic for Sunday
            if 'Su' in str(hours) and 'Su off' not in str(hours):
                sunday_open += 1
            elif '24/7' in str(hours):
                sunday_open += 1
    
    earliest_time = min(all_times) if all_times else "Not Available"
    latest_time = max(all_times) if all_times else "Not Available"
    
    return {
        "Total API Records": total_api_records,
        "Total Unique Businesses": len(df),
        "Total Businesses by Category": df["Business Category"].value_counts().to_dict(),
        "Businesses with Phone Numbers": len(df[df["Phone Number"] != "Not Available"]),
        "Businesses with Websites": len(df[df["Website"] != "Not Available"]),
        "Businesses with Opening Hours": len(df[df["Opening Hours"] != "Not Available"]),
        "Businesses without Contact Info": len(df[
            (df["Phone Number"] == "Not Available") & 
            (df["Website"] == "Not Available") & 
            (df["Email Address"] == "Not Available")
        ]),
        "Earliest Opening Time": earliest_time,
        "Latest Closing Time": latest_time,
        "Businesses Open on Sunday": sunday_open
    }