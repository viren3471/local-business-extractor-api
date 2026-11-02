import pandas as pd
import os
from datetime import datetime
from openpyxl.styles import Font

class ExcelService:
    EXPORT_DIR = "exports"

    @staticmethod
    def generate_excel(df: pd.DataFrame, category: str, city: str, analytics: dict) -> str:
        """Generates a formatted, multi-sheet Excel workbook for the search results."""
        if not os.path.exists(ExcelService.EXPORT_DIR):
            os.makedirs(ExcelService.EXPORT_DIR)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_category = category.replace(' ', '_').replace('/', '_')
        filename = f"{safe_category}_in_{city}_{timestamp}.xlsx"
        filepath = os.path.join(ExcelService.EXPORT_DIR, filename)

        # Prepare Sheet 2: Summary
        summary_data = {
            "Search Category": category,
            "Search City": city,
            "Search Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total API Records": analytics.get("Total API Records", 0),
            "Total Unique Businesses": analytics.get("Total Unique Businesses", 0),
            "Available Phone Numbers": analytics.get("Businesses with Phone Numbers", 0),
            "Available Websites": analytics.get("Businesses with Websites", 0),
            "Available Opening Hours": analytics.get("Businesses with Opening Hours", 0)
        }
        summary_df = pd.DataFrame(list(summary_data.items()), columns=["Metric", "Value"])

        # Prepare Sheet 3: Data Analysis
        analysis_data = {
            "Metric": [
                "Businesses without Contact Info",
                "Earliest Opening Time",
                "Latest Closing Time",
                "Businesses Open on Sunday"
            ],
            "Value": [
                analytics.get("Businesses without Contact Info", 0),
                analytics.get("Earliest Opening Time", "Not Available"),
                analytics.get("Latest Closing Time", "Not Available"),
                analytics.get("Businesses Open on Sunday", 0)
            ]
        }
        
        # Add dynamic category breakdown to the analysis sheet
        categories = analytics.get("Total Businesses by Category", {})
        for cat, count in categories.items():
            analysis_data["Metric"].append(f"Category: {cat}")
            analysis_data["Value"].append(count)
            
        analysis_df = pd.DataFrame(analysis_data)

        # Write to Excel using openpyxl engine
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # 1. Write the three sheets
            df.to_excel(writer, sheet_name="Business Details", index=False)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            analysis_df.to_excel(writer, sheet_name="Data Analysis", index=False)

            # 2. Apply Professional Formatting
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                
                # Freeze the top header row for easy scrolling
                worksheet.freeze_panes = "A2"
                
                for col in worksheet.columns:
                    max_length = 0
                    column_letter = col[0].column_letter
                    
                    for cell in col:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    
                    # Auto-adjust width with padding, cap at width of 50
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                    
                    # Bold the header row
                    col[0].font = Font(bold=True)

        return filepath