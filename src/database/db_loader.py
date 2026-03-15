import pandas as pd
import psycopg2
from psycopg2 import extras
import os
from dotenv import load_dotenv
import ast

load_dotenv()

# Database credentials from .env
DB_NAME = os.getenv("DB_NAME", "job_intelligence")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

def load_data_to_dw(csv_path):
    """Loads processed jobs and skills into the normalized PostgreSQL schema."""
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    # Convert 'skills' column back to actual lists
    df['skills'] = df['skills'].apply(ast.literal_eval)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # 1. Insert Jobs
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO jobs (job_id, title, company, location, description, source, posted_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    company = EXCLUDED.company;
            """, (row['id'], row['title'], row['company'], row['location'], row['description'], row['source'], row['posted_date']))

        # 2. Insert Skills and Mapping
        for _, row in df.iterrows():
            job_id = row['id']
            skills = row['skills']
            
            for skill in skills:
                # Insert skill into master list if not exists
                cur.execute("INSERT INTO skills (skill_name) VALUES (%s) ON CONFLICT (skill_name) DO NOTHING", (skill,))
                
                # Get skill_id
                cur.execute("SELECT skill_id FROM skills WHERE skill_name = %s", (skill,))
                skill_id = cur.fetchone()[0]
                
                # Map job to skill
                cur.execute("INSERT INTO job_skills (job_id, skill_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (job_id, skill_id))

        conn.commit()
        print(f"Successfully loaded {len(df)} jobs into the Data Warehouse.")

    except Exception as e:
        conn.rollback()
        print(f"Failed to load data to DB: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    PROCESSED_DATA = "../../data/processed/processed_jobs.csv"
    load_data_to_dw(PROCESSED_DATA)
