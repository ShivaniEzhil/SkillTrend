import json
import os
import pandas as pd
import re
from skill_taxonomy import SKILL_TAXONOMY

def extract_skills(description):
    """Extracts skills from a job description based on the taxonomy."""
    found_skills = []
    if not description:
        return found_skills
    
    desc_lower = description.lower()
    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            # Using regex to find whole words to avoid partial matches (e.g., 'go' in 'good')
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, desc_lower):
                found_skills.append(skill)
    return list(set(found_skills))

def process_raw_data():
    """
    Processes all JSON files in data/raw,
    removes duplicate jobs,
    extracts skills,
    and saves a clean CSV.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.abspath(os.path.join(base_dir, "../../data/raw"))
    processed_dir = os.path.abspath(os.path.join(base_dir, "../../data/processed"))

    os.makedirs(processed_dir, exist_ok=True)

    all_jobs = []

    json_files = sorted(
        [
            f for f in os.listdir(raw_dir)
            if f.endswith(".json")
        ]
    )

    for filename in json_files:

        file_path = os.path.join(raw_dir, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            if isinstance(data, list):
                all_jobs.extend(data)

    if not all_jobs:
        print("No raw data found.")
        return

    df = pd.DataFrame(all_jobs)

    print(f"Jobs before deduplication : {len(df)}")

    if "id" not in df.columns:
        raise ValueError("Missing 'id' column in extracted data.")

    # Keep only the newest copy of each job
    df = df.drop_duplicates(subset=["id"], keep="last")
    df = df.reset_index(drop=True)

    print(f"Jobs after deduplication  : {len(df)}")

    # Remove rows with no description
    df["description"] = df["description"].fillna("")
    df["skills"] = df["description"].apply(extract_skills)

    output_path = os.path.join(
        processed_dir,
        "processed_jobs.csv"
    )

    df.to_csv(output_path, index=False)

    print(f"\nProcessed {len(df)} unique jobs.")
    print(f"Saved to {output_path}")

    return df

# ==============================
# Main Entry Point
# ==============================

if __name__ == "__main__":
    process_raw_data()