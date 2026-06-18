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
    """Processes all JSON files in data/raw and saves to data/processed."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.abspath(os.path.join(base_dir, "../../data/raw"))
    processed_dir = os.path.abspath(os.path.join(base_dir, "../../data/processed"))
    os.makedirs(processed_dir, exist_ok=True)
    
    all_jobs = []
    
    for filename in os.listdir(raw_dir):
        if filename.endswith(".json"):
            with open(os.path.join(raw_dir, filename), 'r') as f:
                data = json.load(f)
                all_jobs.extend(data)
    
    if not all_jobs:
        print("No raw data found to process.")
        return

    df = pd.DataFrame(all_jobs)
    df['skills'] = df['description'].apply(extract_skills)
    
    # Save processed data
    output_path = os.path.join(processed_dir, "processed_jobs.csv")
    df.to_csv(output_path, index=False)
    print(f"Processed {len(df)} jobs and saved to {output_path}")
    return df

if __name__ == "__main__":
    process_raw_data()
