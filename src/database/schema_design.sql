-- schema_design.sql

-- 1. Create the 'jobs' table to store job metadata
CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    source VARCHAR(50),
    posted_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create the 'skills' table to store unique technical skills
CREATE TABLE IF NOT EXISTS skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL
);

-- 3. Create the 'job_skills' junction table for MANY-TO-MANY relationship
CREATE TABLE IF NOT EXISTS job_skills (
    job_id VARCHAR(50) REFERENCES jobs(job_id) ON DELETE CASCADE,
    skill_id INT REFERENCES skills(skill_id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_job_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_skill_name ON skills(skill_name);

-- 4. Analytical Views for Reporting (Streamlit / Power BI)

DROP VIEW IF EXISTS vw_skill_demand CASCADE;
DROP VIEW IF EXISTS vw_location_demand CASCADE;
DROP VIEW IF EXISTS vw_company_hiring CASCADE;
DROP VIEW IF EXISTS vw_daily_job_trend CASCADE;

-- View 1: vw_skill_demand
CREATE OR REPLACE VIEW vw_skill_demand AS
SELECT
    s.skill_name,
    COUNT(js.job_id) AS demand_count
FROM skills s
JOIN job_skills js ON s.skill_id = js.skill_id
GROUP BY s.skill_name
ORDER BY demand_count DESC;

-- View 2: vw_location_demand
CREATE OR REPLACE VIEW vw_location_demand AS
SELECT
    location,
    COUNT(*) AS total_jobs
FROM jobs
WHERE location IS NOT NULL AND location <> ''
GROUP BY location
ORDER BY total_jobs DESC;

-- View 3: vw_company_hiring
CREATE OR REPLACE VIEW vw_company_hiring AS
SELECT
    TRIM(company) AS company,
    COUNT(*) AS hiring_count
FROM jobs
WHERE company IS NOT NULL AND TRIM(company) <> ''
GROUP BY TRIM(company)
ORDER BY hiring_count DESC;

-- View 4: vw_daily_job_trend
CREATE OR REPLACE VIEW vw_daily_job_trend AS
SELECT
    DATE(posted_date) AS posted_day,
    COUNT(*) AS jobs_posted
FROM jobs
WHERE posted_date IS NOT NULL
GROUP BY DATE(posted_date)
ORDER BY posted_day;
