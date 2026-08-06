import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="India Job Aggregator - Sarkari & Private", page_icon="💼", layout="wide")

st.title("💼 India Job Aggregator Dashboard")
st.markdown("### Sarkari Naukri, Private Jobs, IT & All Categories - Ek Hi Jagah!")

def init_db():
    os.makedirs("data", exist_ok=True)
    db_path = "data/jobs.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            category TEXT,
            company_or_board TEXT,
            qualification TEXT,
            location TEXT,
            source TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_jobs = [
            ("UPSC Civil Services (IAS/IPS) Exam", "Government / Class 1", "UPSC", "Graduate", "All India", "SarkariResult"),
            ("SBI Probationary Officer (PO)", "Banking / Government", "State Bank of India", "Graduate", "All India", "IBPS/SBI"),
            ("SSC CGL Assistant Audit Officer", "Government / Class 1", "Staff Selection Commission", "Graduate", "All India", "SSC Portal"),
            ("Railway NTPC Graduate & Undergraduate", "Government", "Indian Railways", "10th / 12th / Graduate", "Multiple States", "RRB"),
            ("Software Engineer - Python/Django", "Private IT", "TCS / Infosys", "B.Tech / MCA", "Bangalore / Remote", "Naukri"),
            ("Data Analyst", "Private IT", "Amazon / Flipkart", "Graduate", "Hyderabad / Pune", "LinkedIn"),
            ("Data Entry Operator", "Private / Admin", "Local Enterprises", "12th Pass", "Delhi / Mumbai", "Indeed"),
            ("Delivery Executive / Logistics", "Private / Field", "Zepto / Blinkit / Swiggy", "10th Pass", "Pan India", "Direct Walk-in"),
            ("Junior Software Developer", "Private IT", "Startup Tech", "B.Tech / BCA", "Remote", "Wellfound"),
            ("Customer Support Executive", "Private", "Teleperformance", "12th / Graduate", "Noida / Gurgaon", "Monster India")
        ]
        cursor.executemany("INSERT INTO jobs (job_title, category, company_or_board, qualification, location, source) VALUES (?, ?, ?, ?, ?, ?)", sample_jobs)
        conn.commit()
    
    conn.close()

init_db()

db_path = "data/jobs.db"
conn = sqlite3.connect(db_path)
df = pd.read_sql("SELECT * FROM jobs", conn)
conn.close()

st.success(f"Database successfully loaded! Total Active Jobs: {len(df)}")

st.sidebar.header("🔍 Filter Jobs")
selected_category = st.sidebar.selectbox("Filter by Category", ["All"] + list(df["category"].unique()))

if selected_category != "All":
    df = df[df["category"] == selected_category]

search_query = st.text_input("🔎 Search by Job Title, Company, Qualification, or Location:")
if search_query:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

st.dataframe(df.drop(columns=["id"]), use_container_width=True)

st.markdown("---")
st.info("💡 Yeh app automatic database create karta hai. Jaise-jaise naye scrapers ya data add honge, yeh list aur badi hoti jayegi!")
