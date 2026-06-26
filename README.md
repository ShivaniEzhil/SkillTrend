# 🚀 Tech Job Market Intelligence Pipeline

## 📌 Project Overview

The **Tech Job Market Intelligence Pipeline** is an end-to-end **Data Engineering** project that automates the collection, processing, storage, and visualization of technology job market data. It extracts job postings from the Adzuna API, processes and deduplicates the data, stores it in a **Neon PostgreSQL** cloud database, and presents interactive analytics through a **Streamlit dashboard**.

The project demonstrates a complete modern ETL pipeline with cloud database integration, automated workflows, data warehousing, and business intelligence visualization.

---

# ✨ Features

* 🔄 Automated daily ETL pipeline using GitHub Actions
* ☁️ Cloud-hosted PostgreSQL database (Neon)
* 📥 Real-time job extraction using the Adzuna API
* 🧹 Automatic duplicate detection and removal
* 🏗 Normalized PostgreSQL data warehouse
* 📊 Interactive Streamlit dashboard
* 📈 SQL Views for analytics
* 🔐 Secure environment variable management
* ⚡ Bulk data loading using optimized PostgreSQL inserts

---

# 🏗 System Architecture

```
                +----------------+
                |  Adzuna API    |
                +-------+--------+
                        |
                        v
             Raw JSON Data Lake
                 (data/raw)
                        |
                        v
          ETL Processing & Cleaning
         - Skill Extraction
         - Duplicate Removal
                        |
                        v
         Processed Dataset (CSV)
       data/processed/processed_jobs.csv
                        |
                        v
      Bulk Loader (execute_values)
                        |
                        v
       Neon PostgreSQL Data Warehouse
                        |
          SQL Views (Analytics Layer)
                        |
                        v
          Streamlit Interactive Dashboard
```

---

# 📂 Project Structure

```
SkillTrend/
│
├── .github/
│   └── workflows/
│       └── daily_etl.yml
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── extraction/
│   │   ├── adzuna_extractor.py
│   │   └── mock_extractor.py
│   │
│   ├── processing/
│   │   ├── processor.py
│   │   └── skill_taxonomy.py
│   │
│   ├── database/
│   │   ├── db_loader.py
│   │   └── schema_design.sql
│   │
│   └── dashboard/
│       └── app.py
│
├── tests/
│   ├── verify_views.py
│   └── test_pipeline.py
│
├── requirements.txt
├── README.md
└── .env.example
```

---

# ⚙️ ETL Pipeline

## 1. Data Extraction

* Retrieves live job postings from the Adzuna API
* Saves raw responses as JSON files
* Supports mock data for development

---

## 2. Data Processing

The processor:

* Merges all raw JSON files
* Removes duplicate job postings
* Extracts technical skills using regex
* Maps skills using a custom taxonomy
* Generates a clean processed dataset

Output:

```
data/processed/processed_jobs.csv
```

---

## 3. Database Loading

The loader:

* Initializes the PostgreSQL schema
* Performs bulk inserts using `execute_values()`
* Updates existing jobs automatically
* Creates job-skill relationships
* Synchronizes data with Neon PostgreSQL

---

## 4. Analytics Layer

SQL Views provide precomputed analytics:

* `vw_skill_demand`
* `vw_company_hiring`
* `vw_location_demand`
* `vw_daily_job_trend`

These views power the Streamlit dashboard.

---

# 📊 Dashboard Features

The dashboard provides:

* 📈 Hiring trends over time
* 🔥 Most demanded technical skills
* 🏢 Top hiring companies
* 📍 Geographic hiring distribution
* 🤝 Skill co-occurrence analysis
* 📋 Recent job listings
* 📊 Key hiring metrics

---

# 🛠 Tech Stack

### Programming

* Python

### Data Engineering

* Pandas
* Psycopg2
* PostgreSQL
* Neon Database

### Visualization

* Streamlit
* Plotly

### Cloud & DevOps

* GitHub Actions
* GitHub Secrets
* Python Dotenv

---

# 🚀 Getting Started

## 1. Clone Repository

```bash
git clone https://github.com/ShivaniEzhil/SkillTrend.git

cd SkillTrend
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Create a `.env` file:

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

DB_HOST=your_neon_host
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=your_password
```

---

## 4. Run the ETL Pipeline

### Extract Data

```bash
python src/extraction/adzuna_extractor.py
```

### Process Data

```bash
python src/processing/processor.py
```

### Load into Neon PostgreSQL

```bash
python src/database/db_loader.py
```

---

## 5. Verify Database Views

```bash
python tests/verify_views.py
```

---

## 6. Launch Dashboard

```bash
streamlit run src/dashboard/app.py
```

---

# 🤖 GitHub Actions Automation

The project includes a fully automated CI/CD workflow.

Every day the workflow:

1. Extracts new jobs from the Adzuna API
2. Cleans and deduplicates data
3. Generates the processed dataset
4. Synchronizes the Neon PostgreSQL database
5. Cleans old raw data
6. Commits updated processed data back to the repository

Required GitHub Secrets:

```
ADZUNA_APP_ID
ADZUNA_APP_KEY

DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

---

# 📈 Sample Analytics

The dashboard enables analysis such as:

* Most in-demand programming languages
* Top hiring companies
* Geographic hiring distribution
* Daily hiring trends
* Frequently occurring skill combinations

---

# 📌 Future Enhancements

* Docker support
* Apache Airflow orchestration
* Historical trend forecasting
* Salary analytics
* Power BI integration
* REST API for analytics
* Multi-source job aggregation

---

# 👩‍💻 Author

**Shivani E**

Final Year B.Tech Computer Science Student

SRM Institute of Science and Technology

Passionate about Data Engineering, Cloud Technologies, Analytics, and Software Development.
