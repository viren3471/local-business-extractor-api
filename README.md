Local Business Data Extraction & Analytics API
A robust, full-stack data extraction and analytics system built with FastAPI and Python. This system dynamically aggregates local business data from geographic APIs (OpenStreetMap) and web directories, processes it through a Pandas-based data cleaning pipeline, and generates actionable analytics and automated multi-sheet Excel reports.

Includes a lightweight, vanilla JavaScript frontend for seamless data querying and visualization.

🚀 Key Features
Dynamic Data Extraction: Interacts with the OpenStreetMap Overpass API using optimized QL queries and fault-tolerant server rotation to handle 502/429 limits gracefully.

Data Cleaning Pipeline: Utilizes Pandas to standardize raw JSON responses, remove duplicates, normalize phone numbers, and handle missing geographical fields.

Analytics Engine: Computes summary statistics including the earliest/latest opening hours, Sunday operations, and contact availability metrics.

Automated Excel Reporting: Uses OpenPyXL to generate professional, multi-sheet .xlsx reports (Raw Data, Summary, Analytics) with auto-adjusted column widths and frozen headers.

RESTful API Architecture: Modular backend design separating routing, external services, and utility functions for high maintainability.

Integrated UI: A responsive, single-page HTML/JS interface served natively by FastAPI to query and display tabular data in real time.

🛠️ Tech Stack
Backend Framework: FastAPI, Uvicorn

Data Processing: Pandas

Data Exporting: OpenPyXL

External Requests: Requests, HTTPX, BeautifulSoup4

Frontend: Vanilla HTML5, CSS3, JavaScript (Fetch API)
