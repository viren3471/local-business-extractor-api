def get_osm_tags(category: str) -> str:
    """Maps user business categories to OpenStreetMap Overpass tags."""
    mapping = {
        "ca": '["office"="accountant"]',
        "stock brokers": '["office"="financial"]',
        "real estate brokers": '["office"="estate_agent"]',
        "medical stores": '["shop"~"chemist|medical_supply"]',
        "restaurants": '["amenity"="restaurant"]',
        "it companies": '["office"="it"]',
        "doctors": '["amenity"="doctors"]',
        "hotels": '["tourism"="hotel"]'
    }
    return mapping.get(category.lower(), '["amenity"="business"]') # Fallback