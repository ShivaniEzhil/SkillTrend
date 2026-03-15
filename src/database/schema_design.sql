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
