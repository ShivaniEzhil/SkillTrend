import sys
import os
import psycopg2
from dotenv import load_dotenv

# Reconfigure stdout/stderr to use UTF-8 encoding on Windows to prevent UnicodeEncodeError with emojis
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

load_dotenv()

# Database credentials from .env
DB_NAME = os.getenv("DB_NAME", "job_intelligence")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def verify_views():
    print(f"Connecting to database '{DB_NAME}' on {DB_HOST}:{DB_PORT}...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
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
        
        cur.close()
        conn.close()
        
        if all_ok:
            print("\n🏆 All views verified successfully!")
            sys.exit(0)
        else:
            print("\n❌ Verification failed for one or more views.")
            sys.exit(1)

    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_views()
