from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
from app.routes.business_routes import router as business_router
# from app.routes.scrape_routes import router as scrape_router # Uncomment if using the scrape route

app = FastAPI(
    title="Anand Local Business Data Extraction API",
    description="Extracts real business data using OpenStreetMap API, cleans it, and generates Excel reports.",
    version="1.0.0"
)

# Register the backend routes
app.include_router(business_router)
# app.include_router(scrape_router) # Uncomment if using the scrape route

# Serve the frontend UI at the root URL
@app.get("/")
def serve_ui():
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": "index.html not found in the root directory."}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}