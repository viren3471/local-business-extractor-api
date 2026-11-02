import requests
from app.utils.category_mapping import get_osm_tags

class OSMService:
    OVERPASS_URL = "http://overpass-api.de/api/interpreter"

    @staticmethod
    def fetch_businesses(category: str, city: str):
        # FIX 1: Automatically format "anand" to "Anand" so OpenStreetMap can find it
        formatted_city = city.strip().title()
        osm_tags = get_osm_tags(category)
        
        # Overpass QL Query: Search within the correctly capitalized city boundary
        query = f"""
        [out:json][timeout:25];
        area[name="{formatted_city}"]->.searchArea;
        (
          node{osm_tags}(area.searchArea);
          way{osm_tags}(area.searchArea);
          relation{osm_tags}(area.searchArea);
        );
        out center;
        """
        
        # FIX 2: Add strict User-Agent and Accept headers to bypass the 406 Error
        headers = {
            'User-Agent': 'AnandLocalBusinessScraper/1.0 (virenkumar.prajapati@gmail.com)',
            'Accept': '*/*'
        }
        
        # Pass the query AND the headers to the API
        response = requests.post(OSMService.OVERPASS_URL, data={'data': query}, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return OSMService._parse_elements(data.get("elements", []))

    @staticmethod
    def _parse_elements(elements):
        results = []
        for el in elements:
            tags = el.get("tags", {})
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            
            # Skip records with no name to maintain data quality
            if not tags.get("name"):
                continue

            results.append({
                "Source Record ID": el.get("id"),
                "Business Name": tags.get("name"),
                "Business Category": tags.get("office", tags.get("amenity", tags.get("shop", "Unknown"))),
                "Phone Number": tags.get("phone", tags.get("contact:phone", "Not Available")),
                "Email Address": tags.get("email", tags.get("contact:email", "Not Available")),
                "Website": tags.get("website", tags.get("contact:website", "Not Available")),
                "Full Address": tags.get("addr:full", "Not Available"),
                "City": tags.get("addr:city", "Not Available"),
                "Postal Code": tags.get("addr:postcode", "Not Available"),
                "Latitude": lat,
                "Longitude": lon,
                "Opening Hours": tags.get("opening_hours", "Not Available"),
                "Google Maps Link": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat and lon else "Not Available",
                "Source Name": "OpenStreetMap"
            })
        return results