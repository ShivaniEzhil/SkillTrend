import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
COUNTRY = "in"  # Use 'us', 'gb', 'in', etc.

def fetch_adzuna_jobs(query="Data Engineer", results_per_page=10):
    """Fetches job postings from the Adzuna API."""
    if not APP_ID or not APP_KEY:
        print("Error: ADZUNA_APP_ID or ADZUNA_APP_KEY not found in environment.")
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Standardize the format to match our pipeline
        jobs = []
        for result in data.get("results", []):
            jobs.append({
                "id": result.get("id"),
                "title": result.get("title"),
                "company": result.get("company", {}).get("display_name"),
                "location": result.get("location", {}).get("display_name"),
                "description": result.get("description"),
                "source": "Adzuna",
                "posted_date": result.get("created")
            })
        return jobs
    except Exception as e:
        print(f"Error fetching data from Adzuna: {e}")
        return []

def save_raw_data(data, source_name):
    """Saves raw data to the data lake (data/raw/)."""
    if not data:
        print("No data to save.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source_name}_{timestamp}.json"
    filepath = os.path.join("data/raw", filename)
    
    os.makedirs("data/raw", exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved {len(data)} raw jobs to {filepath}")

if __name__ == "__main__":
    # Example usage
    print(f"Fetching jobs for {COUNTRY}...")
    jobs = fetch_adzuna_jobs(query="Data Engineer")
    save_raw_data(jobs, "adzuna")
