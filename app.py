import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Job Aggregator India", page_icon="💼", layout="wide")

st.title("💼 Job Aggregator India Dashboard")
st.markdown("Aapka live job portal successfully chal raha hai!")

# Database connection check
db_path = "data/jobs.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql("SELECT * FROM jobs", conn)
        st.success(f"Database connected! Total jobs loaded: {len(df)}")
    except Exception as e:
        df = pd.DataFrame()
        st.error(f"Error reading database table: {e}")
    conn.close()
else:
    st.info("Database file (`data/jobs.db`) abhi repository mein nahi hai, isiliye sample data dikh raha hai.")
    df = pd.DataFrame({
        "Job Title": ["Software Engineer", "Data Analyst", "Python Developer"],
        "Company": ["Google", "Amazon", "Microsoft"],
        "Location": ["Bangalore", "Hyderabad", "Remote"],
        "Source": ["LinkedIn", "Naukri", "Indeed"]
    })

# Search Filter
search_query = st.text_input("🔍 Search jobs (Title, Company, Location):")
if search_query:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

st.dataframe(df, use_container_width=True)
