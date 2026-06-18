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

def create_database_if_not_exists():
    """Connects to default 'postgres' database and creates the target DB if it doesn't exist."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()
        if not exists:
            print(f"Database '{DB_NAME}' does not exist. Creating...")
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating database '{DB_NAME}': {e}")
        print("Make sure your PostgreSQL server is running and the credentials in .env are correct.")
        raise e

def initialize_schema():
    """Executes schema_design.sql to create the database tables if they do not exist."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.abspath(os.path.join(base_dir, "schema_design.sql"))
    
    if not os.path.exists(schema_path):
        print(f"Error: Schema design file not found at {schema_path}")
        return

    print("Initializing database tables...")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        cur.execute(schema_sql)
        conn.commit()
        print("Database schema loaded successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Failed to initialize schema: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Resolve the path to the processed CSV relative to this script's directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROCESSED_DATA = os.path.abspath(os.path.join(BASE_DIR, "../../data/processed/processed_jobs.csv"))
    
    try:
        # 1. Ensure database exists
        create_database_if_not_exists()
        # 2. Ensure schema/tables exist
        initialize_schema()
        # 3. Load processed data into DB
        load_data_to_dw(PROCESSED_DATA)
    except Exception as e:
        print(f"Database sync/load aborted: {e}")
