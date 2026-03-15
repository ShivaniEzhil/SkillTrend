# 🚀 Tech Job Market Intelligence Pipeline

## 📌 Project Overview
The **Tech Job Market Intelligence Pipeline** is a professional-grade Data Engineering project designed to track, analyze, and visualize global tech hiring trends. It automates the collection of job data from APIs, processes it into a searchable data warehouse, and provides interactive insights into skill demand and geographic hiring patterns.

### Why this stands out on a resume:
- **Multi-Source Ingestion**: Handles both mock data (for development) and real-world API data (Adzuna).
- **Data Lake Architecture**: Stores raw JSON data before processing, following industry-standard ELT/ETL patterns.
- **Skill Taxonomy Engine**: Uses a specialized dictionary to categorize raw job descriptions into 60+ technical skills.
- **PostgreSQL Data Warehouse**: Implements a normalized SQL schema (Jobs, Skills, Junction tables).
- **Advanced Analytics**: Visualizes skill co-occurrence (e.g., Python + SQL) and hiring heatmaps.

---

## 🏗 System Architecture
```
[ Job API / Scraper ] -> [ Data Lake (JSON) ] -> [ ETL Processor ] -> [ PostgreSQL (DW) ] -> [ Streamlit Dashboard ]
```

---

## 📁 File Structure & Explanations

### 🟢 Extraction (`src/extraction/`)
- **`mock_extractor.py`**: Generates synthetic job data for testing the pipeline without hitting API limits.
- **`adzuna_extractor.py`**: Connects to the real Adzuna API, fetches current postings, and standardizes them.

### 🔵 Processing (`src/processing/`)
- **`skill_taxonomy.py`**: The "Knowledge Base" containing categories for Languages, Cloud, Databases, and Tools.
- **`processor.py`**: The ETL heart. It reads raw JSON, extracts skills using regex, and generates a structured CSV.

### 🟡 Database (`src/database/`)
- **`schema_design.sql`**: Professional SQL script to initialize the normalized database structure.
- **`db_loader.py`**: Automated loader that maps CSV columns to SQL tables and handles many-to-many relationships.

### 🔴 Dashboard (`src/dashboard/`)
- **`app.py`**: Feature-rich Streamlit application that pulls live data from PostgreSQL.

---

## 🛠 Tech Stack
- **Languages**: Python (Pandas, Requests, Psycopg2, SQLAlchemy)
- **Database**: PostgreSQL
- **Visualization**: Streamlit, Plotly
- **Config**: Python-Dotenv for secure API key management

---

## 🚀 Getting Started

1. **Clone the project** and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Create a `.env` file based on `.env.example` and add your **Adzuna API Keys** and **PostgreSQL** credentials.

3. **Initialize Database**:
   ```bash
   createdb job_intelligence
   psql -d job_intelligence -f src/database/schema_design.sql
   ```

4. **Run the Pipeline**:
   ```bash
   python3 src/extraction/adzuna_extractor.py  # Ingest
   cd src/processing && python3 processor.py   # Process
   cd ../database && python3 db_loader.py       # Load
   ```

6. **Run Tests**:
   Verify the pipeline logic using the unit tests:
   ```bash
   python3 tests/test_pipeline.py
   ```

## 🤖 Daily Automation (CI/CD)
The pipeline is fully automated using **GitHub Actions**. 
- **Schedule**: Runs every day at 00:00 UTC.
- **Workflow**:
  1. Ingests data from Adzuna API.
  2. Processes and cleans data.
  3. Commits the updated `processed_jobs.csv` back to the repository.
- **Monitoring**: You can check the status of daily runs under the **Actions** tab in this GitHub repository.

### Setup for Automation:
To enable the daily scraper in your own fork, add your Adzuna credentials to **Settings > Secrets and variables > Actions**:
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
