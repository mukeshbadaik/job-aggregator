import streamlit as st
import psycopg2
import pandas as pd
import random
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Pan-India Job Aggregator",
    page_icon="🇮🇳",
    layout="wide"
)

# 1. Centralized Cloud Database Connection
def get_cloud_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"],
        sslmode="require"
    )

# 2. Initialize Database Schema
def init_cloud_db():
    try:
        conn = get_cloud_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pan_india_jobs (
                id SERIAL PRIMARY KEY,
                job_title TEXT,
                company TEXT,
                sector TEXT,
                state TEXT,
                qualification TEXT,
                salary TEXT,
                posted_date DATE
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Database Connection Error: {e}")

init_cloud_db()

# 3. Dummy Data Generators for Batch Ingestion
SECTORS = ["Information Technology", "Manufacturing", "Banking & Finance", "Healthcare", "Retail", "EdTech", "Logistics"]
STATES = ["Maharashtra", "Karnataka", "Delhi NCR", "Tamil Nadu", "Telangana", "Gujarat", "Uttar Pradesh", "West Bengal"]
QUALIFICATIONS = ["B.Tech / B.E.", "MBA / PGDM", "B.Sc / M.Sc", "Diploma", "B.Com / M.Com", "Any Graduate", "12th Pass"]
TITLES = ["Software Engineer", "Data Analyst", "Operations Manager", "HR Executive", "Business Development Manager", "Cloud Architect", "Customer Support Specialist"]
COMPANIES = ["TCS", "Infosys", "Reliance Industries", "Wipro", "HDFC Bank", "Tata Motors", "Flipkart", "Zomato", "Airtel"]

def generate_job_batch(batch_size):
    data = []
    for _ in range(batch_size):
        title = random.choice(TITLES)
        company = random.choice(COMPANIES)
        sector = random.choice(SECTORS)
        state = random.choice(STATES)
        qual = random.choice(QUALIFICATIONS)
        salary = f"₹{random.randint(3, 25)} LPA"
        posted_date = datetime.now().date() - timedelta(days=random.randint(0, 30))
        data.append((title, company, sector, state, qual, salary, posted_date))
    return data

def insert_jobs_to_db(records):
    conn = get_cloud_connection()
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO pan_india_jobs (job_title, company, sector, state, qualification, salary, posted_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, records)
    conn.commit()
    cur.close()
    conn.close()

# 4. Frontend UI Layout
st.title("🇮🇳 Pan-India Enterprise Job Aggregator")
st.markdown("Real-time scalable job portal connected securely to Supabase PostgreSQL.")

# Sidebar Controls for Live Ingestion
st.sidebar.header("🚀 Live Ingestion Control")
batch_count = st.sidebar.selectbox("Select Batch Size", [500, 1000, 5000, 10000])
if st.sidebar.button("Simulate & Insert Batch"):
    with st.spinner(f"Generating and inserting {batch_count} records..."):
        batch_data = generate_job_batch(batch_count)
        insert_jobs_to_db(batch_data)
        st.sidebar.success(f"Successfully added {batch_count} jobs!")
        st.rerun()

# Fetch Data for Filters & Display
@st.cache_data(ttl=60)
def fetch_jobs():
    try:
        conn = get_cloud_connection()
        query = "SELECT job_title, company, sector, state, qualification, salary, posted_date FROM pan_india_jobs ORDER BY posted_date DESC;"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

df_jobs = fetch_jobs()

if not df_jobs.empty:
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filter Jobs")
    
    selected_state = st.sidebar.selectbox("Filter by State", ["All"] + list(df_jobs["state"].unique()))
    selected_sector = st.sidebar.selectbox("Filter by Sector", ["All"] + list(df_jobs["sector"].unique()))
    selected_qual = st.sidebar.selectbox("Filter by Qualification", ["All"] + list(df_jobs["qualification"].unique()))

    # Apply Filters
    filtered_df = df_jobs.copy()
    if selected_state != "All":
        filtered_df = filtered_df[filtered_df["state"] == selected_state]
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df["sector"] == selected_sector]
    if selected_qual != "All":
        filtered_df = filtered_df[filtered_df["qualification"] == selected_qual]

    st.subheader(f"Available Openings ({len(filtered_df)} jobs found)")

    # Pagination Logic (30 results per page)
    items_per_page = 30
    total_pages = max(1, (len(filtered_df) + items_per_page - 1) // items_per_page)
    
    page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    paginated_df = filtered_df.iloc[start_idx:end_idx]

    # Render Table
    st.dataframe(paginated_df, use_container_width=True)
else:
    st.info("Database is currently empty. Use the sidebar **Live Ingestion Control** to inject sample jobs.")
