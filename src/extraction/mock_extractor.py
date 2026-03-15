import json
import os
from datetime import datetime

def save_raw_data(data, source_name):
    """Saves raw data to the data lake (data/raw/)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source_name}_{timestamp}.json"
    filepath = os.path.join("data/raw", filename)
    
    os.makedirs("data/raw", exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved raw data to {filepath}")

def get_mock_jobs():
    """Generates mock job data for testing."""
    return [
        {
            "id": "job_001",
            "title": "Senior Data Engineer",
            "company": "TechCorp",
            "location": "Bangalore",
            "description": "We need a Data Engineer with expertise in Python, SQL, and AWS. Experience with Airflow and Spark is a plus.",
            "source": "MockSource",
            "posted_date": "2026-03-10"
        },
        {
            "id": "job_002",
            "title": "Machine Learning Engineer",
            "company": "AI Innovators",
            "location": "San Francisco",
            "description": "Looking for an ML engineer proficient in Python, PyTorch, and GCP. Knowledge of BigQuery and Kafka required.",
            "source": "MockSource",
            "posted_date": "2026-03-12"
        },
        {
            "id": "job_003",
            "title": "Data Analyst",
            "company": "DataInsights",
            "location": "London",
            "description": "Seeking a Data Analyst with strong SQL and Tableau skills. Experience with Snowflake preferred.",
            "source": "MockSource",
            "posted_date": "2026-03-14"
        }
    ]

if __name__ == "__main__":
    jobs = get_mock_jobs()
    save_raw_data(jobs, "mock_ads")
