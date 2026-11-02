from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from app.services.osm_service import OSMService
from app.utils.data_cleaning import clean_business_data, generate_analytics
from app.services.excel_service import ExcelService
import os

router = APIRouter()

def _get_processed_data(category: str, city: str):
    """Helper function to fetch and process data for multiple endpoints."""
    try:
        raw_data = OSMService.fetch_businesses(category, city)
        total_raw = len(raw_data)
        df = clean_business_data(raw_data)
        analytics = generate_analytics(df, total_raw)
        return df, analytics
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"External API Error: {str(e)}")

@router.get("/api/search")
def search_businesses(category: str = Query(..., description="Business category (e.g., CA, Doctors)"), 
                      city: str = Query("Anand", description="City to search in")):
    df, analytics = _get_processed_data(category, city)
    return {
        "status": "success",
        "message": f"Successfully retrieved {analytics.get('Total Unique Businesses', 0)} unique records.",
        "analytics": analytics,
        "data": df.to_dict(orient="records")
    }

@router.get("/api/businesses")
def get_businesses(category: str, city: str = "Anand"):
    df, _ = _get_processed_data(category, city)
    return {"status": "success", "data": df.to_dict(orient="records")}

@router.get("/api/analytics/summary")
def get_analytics_summary(category: str, city: str = "Anand"):
    _, analytics = _get_processed_data(category, city)
    return {"status": "success", "summary": analytics}

@router.get("/api/analytics/opening-hours")
def get_opening_hours_analysis(category: str, city: str = "Anand"):
    _, analytics = _get_processed_data(category, city)
    return {
        "status": "success",
        "opening_hours_analysis": {
            "Total With Hours": analytics.get("Businesses with Opening Hours"),
            "Earliest Opening": analytics.get("Earliest Opening Time"),
            "Latest Closing": analytics.get("Latest Closing Time"),
            "Open on Sunday": analytics.get("Businesses Open on Sunday")
        }
    }

@router.get("/api/export")
def export_excel(category: str, city: str = "Anand"):
    df, analytics = _get_processed_data(category, city)
    if df.empty:
        raise HTTPException(status_code=404, detail="No businesses found for this category and city.")
        
    try:
        filepath = ExcelService.generate_excel(df, category, city, analytics)
        return FileResponse(
            path=filepath, 
            filename=os.path.basename(filepath), 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation failed: {str(e)}")

@router.get("/api/categories")
def get_categories():
    return {
        "status": "success",
        "supported_categories": [
            "CA", "Stock Brokers", "Real Estate Brokers", "Medical Stores",
            "Restaurants", "IT Companies", "Doctors", "Hotels"
        ]
    }