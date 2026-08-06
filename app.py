import streamlit as st
import pandas as pd
import psycopg2
import random
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Pan-India Enterprise Job Portal",
    page_icon="💼",
    layout="wide"
)

# Centralized Cloud Database Connection (Transaction Pooler - Port 6543)
def get_cloud_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"],
        sslmode="require"
    )

# Initialize Database Schema
def init_cloud_db():
    try:
        conn = get_cloud_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT,
                sector TEXT,
                state TEXT,
                qualification TEXT,
                salary TEXT,
                start_date DATE,
                last_date DATE,
                total_openings INT DEFAULT 1,
                apply_link TEXT
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Database Connection Error: {e}")

init_cloud_db()

# Dummy Data Generators for Batch Ingestion
SECTORS = ["Information Technology", "Manufacturing", "Banking & Financial", "Healthcare", "E-Commerce"]
STATES = ["Maharashtra", "Karnataka", "Delhi NCR", "Tamil Nadu", "Telangana", "Uttar Pradesh"]
QUALIFICATIONS = ["B.Tech / B.E.", "MBA / PGDM", "B.Sc / M.Sc", "Diploma", "Any Graduate"]
TITLES = ["Software Engineer", "Data Analyst", "Operations Manager", "HR Executive", "Finance Manager"]
COMPANIES = ["TCS", "Infosys", "Reliance Industries", "Wipro", "HDFC Bank", "Tata Motors", "Zomato"]

def generate_job_batch(batch_size):
    data = []
    for _ in range(batch_size):
        title = random.choice(TITLES)
        company = random.choice(COMPANIES)
        sector = random.choice(SECTORS)
        state = random.choice(STATES)
        qual = random.choice(QUALIFICATIONS)
        salary = f"{random.randint(3, 25)} LPA"
        start_date = datetime.now().date() - timedelta(days=random.randint(0, 5))
        last_date = datetime.now().date() + timedelta(days=random.randint(15, 45))
        total_openings = random.randint(1, 15)
        apply_link = "https://www.linkedin.com/jobs/"
        
        data.append((title, company, sector, state, qual, salary, start_date, last_date, total_openings, apply_link))
    return data

def insert_jobs_to_db(records):
    conn = get_cloud_connection()
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO jobs (title, company, sector, state, qualification, salary, start_date, last_date, total_openings, apply_link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, records)
    conn.commit()
    cur.close()
    conn.close()

# Professional UI Layout
st.title("💼 Pan-India Enterprise Job Portal")
st.markdown("Real-time scalable enterprise career portal securely connected to Supabase PostgreSQL.")
st.markdown("---")

# Sidebar Controls for Live Ingestion & Filters
st.sidebar.header("⚙️ Portal Controls")

with st.sidebar.expander("📥 Live Ingestion Panel"):
    batch_count = st.selectbox("Select Batch Size", [500, 1000, 5000])
    if st.button("Simulate & Insert Batch"):
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
        query = "SELECT title, company, sector, state, qualification, salary, start_date, last_date, total_openings, apply_link FROM jobs"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

df_jobs = fetch_jobs()

if not df_jobs.empty:
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filter Job Openings")
    
    selected_state = st.sidebar.selectbox("Filter by State", ["All"] + list(df_jobs["state"].dropna().unique()))
    selected_sector = st.sidebar.selectbox("Filter by Sector", ["All"] + list(df_jobs["sector"].dropna().unique()))
    selected_qual = st.sidebar.selectbox("Filter by Qualification", ["All"] + list(df_jobs["qualification"].dropna().unique()))

    # Apply Filters
    filtered_df = df_jobs.copy()
    if selected_state != "All":
        filtered_df = filtered_df[filtered_df["state"] == selected_state]
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df["sector"] == selected_sector]
    if selected_qual != "All":
        filtered_df = filtered_df[filtered_df["qualification"] == selected_qual]

    st.subheader(f"Available Openings ({len(filtered_df)} jobs found)")

    # Pagination Logic
    items_per_page = 20
    total_pages = max(1, (len(filtered_df) + items_per_page - 1) // items_per_page)
    
    page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    paginated_df = filtered_df.iloc[start_idx:end_idx]

    # Render Professional Table/Data View
    st.dataframe(
        paginated_df,
        use_container_width=True,
        column_config={
            "title": "Job Title",
            "company": "Company",
            "sector": "Sector",
            "state": "State",
            "qualification": "Qualification",
            "salary": "Salary Package",
            "start_date": "Start Date",
            "last_date": "Last Date",
            "total_openings": "Openings",
            "apply_link": st.column_config.LinkColumn("Apply Link")
        }
    )
else:
    st.info("Database is currently empty. Use the sidebar **'Live Ingestion Panel'** to populate data.")
