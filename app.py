import sqlite3
import pandas as pd
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="India Master Job Aggregator Dashboard",
    page_icon="🇮🇳",
    layout="wide",
)

DB_PATH = "data/jobs.db"

# List of all 28 States and 8 UTs of India
INDIAN_STATES = [
    "All India",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
]

QUALIFICATION_LEVELS = [
    "All Qualifications",
    "No Certificate / Open (Helper, Delivery, Labor)",
    "10th Pass",
    "12th Pass",
    "Certificate / ITI / Diploma",
    "Graduate & Above",
    "Professional / Technical (B.Tech, CA, MBBS)",
]


# Initialize Database with Auto-Migration for Missing Columns
def init_db():
  import os

  os.makedirs("data", exist_ok=True)
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  # Create table if it doesn't exist
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            company TEXT,
            qualification TEXT,
            certificate_needed TEXT,
            requirements TEXT,
            state TEXT,
            job_type TEXT,
            start_date TEXT,
            last_date TEXT,
            apply_link TEXT,
            source TEXT,
            location TEXT
        )
    """)
  conn.commit()

  # Check if any column is missing in an existing database and add it safely
  cursor.execute("PRAGMA table_info(jobs)")
  existing_columns = [col[1] for col in cursor.fetchall()]

  required_columns = {
      "job_title": "TEXT",
      "company": "TEXT",
      "qualification": "TEXT",
      "certificate_needed": "TEXT",
      "requirements": "TEXT",
      "state": "TEXT",
      "job_type": "TEXT",
      "start_date": "TEXT",
      "last_date": "TEXT",
      "apply_link": "TEXT",
      "source": "TEXT",
      "location": "TEXT",
  }

  for col, col_type in required_columns.items():
    if col not in existing_columns:
      cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col} {col_type}")
  conn.commit()

  # Insert master data if table is empty
  cursor.execute("SELECT COUNT(*) FROM jobs")
  if cursor.fetchone()[0] == 0:
    master_jobs = [
        (
            "Delivery Executive / Partner",
            "Zomato / Blinkit",
            "No Certificate / Open (Helper, Delivery, Labor)",
            "None (Aadhaar Card & Driving License/Cycle)",
            "Smartphone, Bank Account, Age 18+",
            "All India",
            "Private",
            "2026-01-01",
            "Open 365 Days",
            "https://www.zomato.com/delivery",
            "Direct Partner",
            "Pan India",
        ),
        (
            "Postal Gramin Dak Sevak (GDS)",
            "India Post",
            "10th Pass",
            "10th Class Marksheet with Math & English",
            "Basic computer knowledge, Cycling proficiency",
            "All India",
            "Sarkari",
            "2026-06-01",
            "2026-06-30",
            "https://indiapostgdsonline.gov.in",
            "India Post",
            "All Districts",
        ),
        (
            "Odisha Police Constable Recruitment",
            "Odisha Police",
            "12th Pass",
            "12th Pass Certificate + Physical Fitness",
            "Valid height, running test standards as per Odisha Police norms",
            "Odisha",
            "Sarkari",
            "2026-06-10",
            "2026-07-15",
            "https://odishapolice.gov.in",
            "Odisha Police",
            "Multiple Districts",
        ),
        (
            "ITI Electrician / Fitter Apprentice",
            "NTPC Limited",
            "Certificate / ITI / Diploma",
            "ITI Certificate in Electrician/Fitter trade",
            "NCVT/SCVT registration, Age 18-28 years",
            "Odisha",
            "Sarkari",
            "2026-06-01",
            "2026-06-25",
            "https://ntpc.co.in",
            "NTPC Portal",
            "Talcher, Odisha",
        ),
        (
            "Software Engineer - Python",
            "Tech Mahindra",
            "Professional / Technical (B.Tech, CA, MBBS)",
            "B.Tech / MCA Degree",
            "Strong knowledge of Python, Django, SQL",
            "Karnataka",
            "Private",
            "2026-06-05",
            "2026-07-10",
            "https://www.techmahindra.com/careers",
            "Naukri",
            "Bangalore",
        ),
    ]
    cursor.executemany(
        """
            INSERT INTO jobs (job_title, company, qualification, certificate_needed, requirements, state, job_type, start_date, last_date, apply_link, source, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        master_jobs,
    )
    conn.commit()
  conn.close()


# Live Sync Function
def fetch_and_add_live_jobs():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  scraped_jobs = []
  try:
    response = requests.get(
        "https://www.arbeitnow.com/api/job-board-api", timeout=10
    )
    if response.status_code == 200:
      data = response.json().get("data", [])
      for item in data[:8]:
        title = item.get("title", "Job Title")
        company = item.get("company_name", "Private Company")
        url = item.get("url", "https://www.arbeitnow.com")
        location = item.get("location", "India / Remote")
        scraped_jobs.append(
            (
                title,
                company,
                "Professional / Technical (B.Tech, CA, MBBS)",
                "Graduation Degree",
                "Good communication and technical skills",
                "All India",
                "Private",
                "2026-06-01",
                "Ongoing",
                url,
                "Live API",
                location,
            )
        )
  except Exception as e:
    pass

  added_count = 0
  for job in scraped_jobs:
    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE job_title = ? AND company = ?",
        (job[0], job[1]),
    )
    if cursor.fetchone()[0] == 0:
      cursor.execute(
          """
                INSERT INTO jobs (job_title, company, qualification, certificate_needed, requirements, state, job_type, start_date, last_date, apply_link, source, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
          job,
      )
      added_count += 1

  conn.commit()
  conn.close()
  return added_count


# Initialize Database
init_db()

# --- UI Layout ---
st.title("🇮🇳 India Master Job Aggregator Dashboard")
st.markdown(
    "Complete tracking platform with **Start Dates, Last Dates, Eligibility,"
    " and Direct Apply Links**."
)

# Sidebar Filters
st.sidebar.header("🎛️ Master Search Filters")

if st.sidebar.button("🔄 Sync Live Vacancies"):
  with st.spinner("Syncing latest pan-India opportunities..."):
    count = fetch_and_add_live_jobs()
  st.sidebar.success(f"Synced {count} new entries!")
  st.rerun()

job_category = st.sidebar.radio(
    "Sector:", ["All Jobs", "Sarkari", "Private"]
)
selected_state = st.sidebar.selectbox("State / UT:", INDIAN_STATES)
selected_qualification = st.sidebar.selectbox(
    "Qualification Level:", QUALIFICATION_LEVELS
)

# Load Database
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM jobs", conn)
conn.close()

# Apply Filters Safely
if not df.empty and "job_type" in df.columns:
  if job_category != "All Jobs":
    df = df[df["job_type"] == job_category]

  if selected_state != "All India":
    df = df[df["state"] == selected_state]

  if selected_qualification != "All Qualifications":
    df = df[df["qualification"] == selected_qualification]

# Global Search Bar
search_query = st.text_input(
    "🔎 Search by Job, Company, Skill, or Location:"
)
if search_query and not df.empty:
  df = df[
      df["job_title"].str.contains(search_query, case=False, na=False)
      | df["company"].str.contains(search_query, case=False, na=False)
      | df["qualification"].str.contains(search_query, case=False, na=False)
      | df["requirements"].str.contains(search_query, case=False, na=False)
      | df["location"].str.contains(search_query, case=False, na=False)
  ]

# Metrics
c1, c2, c3 = st.columns(3)
c1.metric("Matching Jobs Available", len(df) if not df.empty else 0)
c2.metric(
    "Sarkari Openings",
    (
        len(df[df["job_type"] == "Sarkari"])
        if not df.empty and "job_type" in df.columns
        else 0
    ),
)
c3.metric(
    "Private Openings",
    (
        len(df[df["job_type"] == "Private"])
        if not df.empty and "job_type" in df.columns
        else 0
    ),
)

st.markdown("---")

# Detailed View / Cards with Start Date, Last Date & Apply Links
if not df.empty:
  st.subheader("📋 Available Job Openings & Requirements")
  for idx, row in df.iterrows():
    with st.expander(f"📌 {row['job_title']} — {row['company']} ({row['state']})"):
      col_a, col_b = st.columns(2)
      with col_a:
        st.write(f"**Sector / Type:** {row.get('job_type', 'N/A')}")
        st.write(f"**Location:** {row.get('location', 'N/A')}")
        st.write(f"**Qualification Required:** {row.get('qualification', 'N/A')}")
        st.write(f"**Certificate Needed:** {row.get('certificate_needed', 'N/A')}")
      with col_b:
        st.write(f"**Eligibility / Requirements:** {row.get('requirements', 'N/A')}")
        st.write(f"**Start Date:** 🚀 {row.get('start_date', 'N/A')}")
        st.write(f"**Last Date to Apply:** ⏰ {row.get('last_date', 'N/A')}")
        st.write(f"**Source Platform:** {row.get('source', 'N/A')}")

      # Direct Clickable Apply Link Button
      st.markdown(
          f"👉 **[Click Here to Apply / View Official Notice]"
          f"({row.get('apply_link', '#')})**",
          unsafe_allow_html=True,
      )
else:
  st.warning(
      "No listings match your selected combination. Try clearing filters or"
      " clicking 'Sync Live Vacancies'."
                                       )
    
