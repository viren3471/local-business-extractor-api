from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from bs4 import BeautifulSoup
import httpx
import os
from app.utils.data_cleaning import clean_business_data, generate_analytics
from app.services.excel_service import ExcelService

router = APIRouter()

@router.get("/api/scrape-directory")
async def scrape_business_directory(
    category: str = "chartered accountants", 
    city: str = "anand"
):
    # Format URL for a directory like Sulekha (e.g., sulekha.com/chartered-accountants/anand)
    search_query = category.lower().replace(" ", "-")
    target_city = city.lower().replace(" ", "-")
    url = f"https://www.sulekha.com/{search_query}/{target_city}"
    
    # Use realistic browser headers to prevent getting blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=20.0, follow_redirects=True)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        extracted_data = []
        
        # Scrape the business listings (Targeting Sulekha's standard list items)
        listings = soup.find_all('li', class_='list-item') 
        
        for idx, listing in enumerate(listings):
            # Extract Business Name
            name_tag = listing.find('h3', class_='title')
            name = name_tag.text.strip() if name_tag else "Not Available"
            
            # Extract Address
            address_tag = listing.find('address')
            address = address_tag.text.strip() if address_tag else "Not Available"
            
            # Extract Phone Number (Often hidden in a 'b' tag or data attribute)
            phone_tag = listing.find('b', class_='contact-number')
            phone = phone_tag.text.strip() if phone_tag else "Not Available"
            
            # Skip empty records
            if name == "Not Available" and phone == "Not Available":
                continue

            extracted_data.append({
                "Source Record ID": f"SUL_{idx}",
                "Business Name": name,
                "Business Category": category.title(),
                "Phone Number": phone,
                "Full Address": address,
                "Email Address": "Not Available",
                "Website": "Not Available",
                "Opening Hours": "Not Available"
            })
            
        if not extracted_data:
             raise HTTPException(status_code=404, detail="No data found. The website structure may have changed, or you were blocked.")

        # Route through our existing cleaning and analytics pipeline
        cleaned_df = clean_business_data(extracted_data)
        analytics = generate_analytics(cleaned_df, len(extracted_data))
        
        # Generate the final formatted Excel workbook
        filepath = ExcelService.generate_excel(cleaned_df, category, city, analytics)
        
        return FileResponse(
            path=filepath, 
            filename=os.path.basename(filepath),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")