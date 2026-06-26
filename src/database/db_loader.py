import os
import ast
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

# ==============================
# Database Configuration
# ==============================

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def get_db_connection():
    """
    Create a secure PostgreSQL connection.
    """

    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode="require",
            connect_timeout=5
        )

    except psycopg2.Error as e:
        raise RuntimeError(
            f"Unable to connect to PostgreSQL:\n{e}"
        )


# ==============================
# Database Schema
# ==============================

def initialize_schema():
    """
    Creates tables/views if they don't already exist.
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, "schema_design.sql")

    if not os.path.exists(schema_path):
        raise FileNotFoundError(schema_path)

    print("Checking database schema...")

    with get_db_connection() as conn:
        with conn.cursor() as cur:

            with open(schema_path, "r", encoding="utf-8") as f:
                cur.execute(f.read())

            conn.commit()

    print("Schema ready.")

def load_data_to_dw(csv_path):
    """
    Load processed jobs into the PostgreSQL warehouse using bulk inserts.
    """

    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    print("Reading processed dataset...")

    df = pd.read_csv(csv_path)
    df["skills"] = df["skills"].apply(
        lambda x: ast.literal_eval(x) if pd.notna(x) else []
    )

    print(f"Loaded {len(df)} jobs.")

    duplicate_count = df.duplicated(subset=["id"]).sum()


    # Remove duplicate job IDs
    df = df.drop_duplicates(subset=["id"], keep="last")

    with get_db_connection() as conn:
        with conn.cursor() as cur:

            # --------------------------------------------------
            # 1. Bulk Insert Jobs
            # --------------------------------------------------

            print("Loading jobs...")

            job_rows = [
                (
                    row.id,
                    row.title,
                    row.company,
                    row.location,
                    row.description,
                    row.source,
                    row.posted_date,
                )
                for row in df.itertuples(index=False)
            ]

            execute_values(
                cur,
                """
                INSERT INTO jobs (
                    job_id,
                    title,
                    company,
                    location,
                    description,
                    source,
                    posted_date
                )
                VALUES %s
                ON CONFLICT (job_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    company = EXCLUDED.company,
                    location = EXCLUDED.location,
                    description = EXCLUDED.description,
                    source = EXCLUDED.source,
                    posted_date = EXCLUDED.posted_date;
                """,
                job_rows,
                page_size=500
            )

            print(f"✓ Loaded {len(job_rows)} jobs.")

            # --------------------------------------------------
            # 2. Collect Unique Skills
            # --------------------------------------------------

            print("Loading skills...")

            unique_skills = sorted({
                skill
                for skills in df["skills"]
                for skill in skills
                if skill
            })

            execute_values(
                cur,
                """
                INSERT INTO skills (skill_name)
                VALUES %s
                ON CONFLICT (skill_name)
                DO NOTHING;
                """,
                [(skill,) for skill in unique_skills],
                page_size=500
            )

            print(f"✓ Loaded {len(unique_skills)} unique skills.")

            # --------------------------------------------------
            # 3. Read Skill IDs Once
            # --------------------------------------------------

            cur.execute(
                """
                SELECT skill_id, skill_name
                FROM skills;
                """
            )

            skill_lookup = {
                skill_name: skill_id
                for skill_id, skill_name in cur.fetchall()
            }

            # --------------------------------------------------
            # 4. Build Job-Skill Mapping
            # --------------------------------------------------

            print("Creating job-skill mappings...")

            mapping_rows = set()

            for row in df.itertuples(index=False):

                for skill in row.skills:

                    if not skill:
                        continue

                    skill_id = skill_lookup.get(skill)

                    if skill_id:
                        mapping_rows.add(
                            (
                                row.id,
                                skill_id
                            )
                        )

            mapping_rows = list(mapping_rows)

            execute_values(
                cur,
                """
                INSERT INTO job_skills (
                    job_id,
                    skill_id
                )
                VALUES %s
                ON CONFLICT DO NOTHING;
                """,
                mapping_rows,
                page_size=1000
            )

            print(f"✓ Loaded {len(mapping_rows)} job-skill mappings.")

            conn.commit()

    print("\nDatabase successfully synchronized.")

# ==============================
# Main Entry Point
# ==============================

if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    PROCESSED_DATA = os.path.abspath(
        os.path.join(BASE_DIR, "../../data/processed/processed_jobs.csv")
    )

    print("=" * 60)
    print("Tech Job Market Intelligence")
    print("Database Synchronization")
    print("=" * 60)

    try:
        initialize_schema()
        load_data_to_dw(PROCESSED_DATA)

        print("\nDatabase synchronization completed successfully.")

    except Exception as e:
        print("\nDatabase synchronization failed.")
        print(e)