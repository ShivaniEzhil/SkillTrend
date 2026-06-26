import sys
import os
import psycopg2
from dotenv import load_dotenv

# Reconfigure stdout/stderr to use UTF-8 encoding on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Load environment variables
load_dotenv()

# Database credentials from .env
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def verify_views():
    print(f"Connecting to database '{DB_NAME}' on {DB_HOST}:{DB_PORT}...")

    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode="require",
            connect_timeout=5
        )

        cur = conn.cursor()

        queries = {
            "vw_skill_demand": "SELECT * FROM vw_skill_demand LIMIT 10;",
            "vw_location_demand": "SELECT * FROM vw_location_demand LIMIT 10;",
            "vw_company_hiring": "SELECT * FROM vw_company_hiring LIMIT 10;",
            "vw_daily_job_trend": "SELECT * FROM vw_daily_job_trend LIMIT 10;"
        }

        all_ok = True

        for view_name, query in queries.items():
            print(f"\nVerifying {view_name}...")

            try:
                cur.execute(query)
                results = cur.fetchall()

                print(f"✅ Query successful. Retrieved {len(results)} rows.")

                for row in results[:3]:
                    print(f"   {row}")

            except Exception as e:
                print(f"❌ Failed to query {view_name}: {e}")
                all_ok = False
                conn.rollback()

        if all_ok:
            print("\n🏆 All views verified successfully!")
            sys.exit(0)
        else:
            print("\n❌ Verification failed for one or more views.")
            sys.exit(1)

    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    verify_views()