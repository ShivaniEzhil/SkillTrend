import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import psycopg2
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Tech Job Market Intelligence", layout="wide")

# Database Connection Helper with CSV Fallback
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="require",
            connect_timeout=5
        )
    except psycopg2.Error:
        st.sidebar.warning("⚠️ PostgreSQL connection unavailable. Switching to CSV mode.")
        return None

# Sidebar Configuration
st.sidebar.title("🛠 Pipeline Controls")
source_filter = st.sidebar.multiselect("Select Job Sources", ["Adzuna", "MockSource"], default=["Adzuna", "MockSource"])

# Main Dashboard Header
st.title("🚀 Tech Job Market Intelligence Pipeline")
st.markdown("---")

# Data Retrieval (SQL with CSV Fallback)
conn = get_db_connection()
if conn:
    st.sidebar.success("✅ Connected to PostgreSQL Data Warehouse")
    
    # 1. Fetch raw data for metrics, co-occurrence, and recent listings
    query_jobs = """
        SELECT j.job_id, j.title, j.company, j.location, j.posted_date, j.source, s.skill_name
        FROM jobs j
        LEFT JOIN job_skills js ON j.job_id = js.job_id
        LEFT JOIN skills s ON js.skill_id = s.skill_id
        WHERE j.source IN %s
    """
    df_raw = pd.read_sql(query_jobs, conn, params=(tuple(source_filter),))
    
    # 2. Fetch pre-aggregated data directly from PostgreSQL views (no source filtering needed)
    skill_df = pd.read_sql(
        "SELECT skill_name AS \"Skill\", demand_count AS \"Count\" FROM vw_skill_demand LIMIT 12",
        conn
    )

    company_counts = pd.read_sql(
        "SELECT company AS \"Company\", hiring_count AS \"Job Count\" FROM vw_company_hiring LIMIT 10",
        conn
    )

    loc_counts = pd.read_sql(
        "SELECT location AS \"Location\", total_jobs AS \"Count\" FROM vw_location_demand",
        conn
    )

    trend_df = pd.read_sql(
        "SELECT posted_day AS \"posted_date\", jobs_posted AS \"Count\" FROM vw_daily_job_trend",
        conn
    )
    trend_df['posted_date'] = pd.to_datetime(trend_df['posted_date']).dt.date
    
    conn.close()
    
    # Group skills back into lists per job
    if not df_raw.empty:
        df = df_raw.groupby(['job_id', 'title', 'company', 'location', 'posted_date', 'source'])['skill_name'].apply(list).reset_index()
    else:
        df = pd.DataFrame()
else:
    st.sidebar.warning("⚠️ PostgreSQL not found. Reading from CSV Data Lake...")
    CSV_PATH = "data/processed/processed_jobs.csv"
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        # Standardize format to match SQL output
        import ast
        df['skill_name'] = df['skills'].apply(ast.literal_eval)
        df['job_id'] = df['id']
        # Filter by source
        df = df[df['source'].isin(source_filter)]
        # Create a flat version for skill counts
        df_raw = df.explode('skill_name')
        
        # Perform identical offline aggregations in Pandas to match the views
        all_skills_offline = [s for s in df_raw['skill_name'] if s]
        skill_counts_offline = Counter(all_skills_offline).most_common(12)
        skill_df = pd.DataFrame(skill_counts_offline, columns=['Skill', 'Count'])
        
        company_counts = df['company'].value_counts().head(10).reset_index()
        company_counts.columns = ['Company', 'Job Count']
        
        loc_counts = df['location'].value_counts().reset_index()
        loc_counts.columns = ['Location', 'Count']
        
        df_clean = df.dropna(subset=['posted_date']).copy()
        df_clean['posted_date'] = df_clean['posted_date'].astype(str).str.strip()
        df_clean['posted_date'] = pd.to_datetime(df_clean['posted_date'], format='mixed', errors='coerce', utc=True)
        df_clean = df_clean.dropna(subset=['posted_date'])
        trend_df = df_clean.groupby(df_clean['posted_date'].dt.date).size().reset_index(name='Count')
    else:
        df = pd.DataFrame()
        df_raw = pd.DataFrame()
        skill_df = pd.DataFrame(columns=['Skill', 'Count'])
        company_counts = pd.DataFrame(columns=['Company', 'Job Count'])
        loc_counts = pd.DataFrame(columns=['Location', 'Count'])
        trend_df = pd.DataFrame(columns=['posted_date', 'Count'])

if not df.empty:
    # Data Processing for Dashboard
    df['skill_count'] = df['skill_name'].apply(lambda x: len([s for s in x if s is not None]))

    # --- Row 1: Key Metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Jobs Analyzed", len(df))
    m2.metric("Unique Skills Found", df_raw['skill_name'].nunique())
    m3.metric("Top Company", df['company'].mode()[0] if not df['company'].empty else "N/A")
    m4.metric("Top Location", df['location'].mode()[0] if not df['location'].empty else "N/A")

    st.markdown("### 📊 Market Insights")
    col1, col2 = st.columns(2)

    # For Candidate Insights, compute global stats
    all_skills = [s for s in df_raw['skill_name'] if s]
    skill_counts = Counter(all_skills).most_common(12)

    with col1:
        st.subheader("🔥 Top Demanded Skills")
        fig_skills = px.bar(skill_df, x='Skill', y='Count', color='Count', template="plotly_dark", color_continuous_scale="Blues")
        st.plotly_chart(fig_skills, use_container_width=True)

    with col2:
        st.subheader("🏢 Top Hiring Companies")
        fig_comp = px.bar(company_counts, y='Company', x='Job Count', orientation='h', template="plotly_dark", color="Job Count")
        st.plotly_chart(fig_comp, use_container_width=True)

    # --- Row 2: Geospatial & Trends ---
    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📍 Job Distribution by City")
        fig_loc = px.pie(loc_counts, names='Location', values='Count', hole=0.5, template="plotly_dark", color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_loc, use_container_width=True)

    with col4:
        st.subheader("📈 Hiring Trend Over Time")
        fig_trend = px.line(trend_df, x='posted_date', y='Count', markers=True, template="plotly_dark", line_shape="spline")
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- Row 3: Skill Co-occurrence Heatmap ---
    st.markdown("---")
    st.subheader("🤝 Skill Bundle Analysis (Co-occurrence)")
    pairs = []
    for x in df['skill_name']:
        skills_list = sorted([s for s in x if s])
        for i in range(len(skills_list)):
            for j in range(i + 1, len(skills_list)):
                pairs.append(tuple(sorted((skills_list[i], skills_list[j]))))
    
    pair_counts = Counter(pairs).most_common(15)
    if pair_counts:
        pair_df = pd.DataFrame([{"Pair": f"{p[0]} + {p[1]}", "Frequency": c} for p, c in pair_counts])
        fig_co = px.bar(pair_df, x='Frequency', y='Pair', orientation='h', template="plotly_dark", color="Frequency")
        st.plotly_chart(fig_co, use_container_width=True)
    else:
        st.info("Not enough skill pairs found for co-occurrence analysis yet.")

    # --- Bonus Feature: Recommendation Insights ---
    st.markdown("---")
    st.subheader("💡 Actionable Insights for Candidates")
    top_3_skills = [s[0] for s in skill_counts[:3]]
    st.success(f"**Market Leader Insights**: The most critical skills right now are **{', '.join(top_3_skills)}**. "
               f"Candidates proficient in these areas have access to **{int((len(all_skills)/len(df))*100)}%** of the analyzed job market.")

    st.subheader("📋 Recent Job Listings")
    st.dataframe(df[['title', 'company', 'location', 'posted_date', 'skill_name', 'source']].sort_values('posted_date', ascending=False), use_container_width=True)


else:
    st.warning("No data found matching the selected filters. Try running the extraction and DB loader first.")

if not conn:
    st.sidebar.info("💡 Note: Running in Offline Mode (CSV). PostgreSQL connection is unavailable.")
