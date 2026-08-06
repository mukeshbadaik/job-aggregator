import sqlite3
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="India Job Aggregator Dashboard", page_icon="🇮🇳", layout="wide"
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


# Initialize Database and Table with State & Job Type
def init_db():
  import os

  os.makedirs("data", exist_ok=True)
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            company TEXT,
            qualification TEXT,
            state TEXT,
            job_type TEXT,
            source TEXT,
            location TEXT
        )
    """)
  conn.commit()

  # Insert comprehensive sample data covering India if table is empty
  cursor.execute("SELECT COUNT(*) FROM jobs")
  if cursor.fetchone()[0] == 0:
    sample_jobs = [
        (
            "UPSC Civil Services Exam",
            "Union Public Service Commission",
            "Graduate",
            "All India",
            "Sarkari",
            "SarkariResult",
            "All India",
        ),
        (
            "SBI Probationary Officer",
            "State Bank of India",
            "Graduate",
            "All India",
            "Sarkari",
            "IBPS/SBI",
            "All India",
        ),
        (
            "BPSC 70th Combined Exam",
            "Bihar Public Service Commission",
            "Graduate",
            "Bihar",
            "Sarkari",
            "BPSC Portal",
            "Patna, Bihar",
        ),
        (
            "UPPSC Staff Nurse Vacancy",
            "Uttar Pradesh PSC",
            "Diploma / GNM",
            "Uttar Pradesh",
            "Sarkari",
            "UPPSC",
            "Lucknow, UP",
        ),
        (
            "MPSC Gazetted Civil Services",
            "Maharashtra PSC",
            "Graduate",
            "Maharashtra",
            "Sarkari",
            "MPSC",
            "Mumbai, Maharashtra",
        ),
        (
            "Software Engineer - Python",
            "Tech Mahindra",
            "B.Tech / MCA",
            "Karnataka",
            "Private",
            "Naukri",
            "Bangalore",
        ),
        (
            "Data Analyst",
            "TCS",
            "Graduate",
            "Telangana",
            "Private",
            "LinkedIn",
            "Hyderabad",
        ),
        (
            "Junior Data Entry Operator",
            "Local E-Commerce Hub",
            "12th Pass",
            "Delhi",
            "Private",
            "Indeed",
            "New Delhi",
        ),
        (
            "Field Delivery Executive",
            "QuickLogistics",
            "10th Pass",
            "West Bengal",
            "Private",
            "Local Walk-in",
            "Kolkata",
        ),
        (
            "Store Assistant / Helper",
            "Retail Chain",
            "10th / 12th",
            "Rajasthan",
            "Private",
            "Monster India",
            "Jaipur",
        ),
    ]
    cursor.executemany(
        """
            INSERT INTO jobs (job_title, company, qualification, state, job_type, source, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        sample_jobs,
    )
    conn.commit()
  conn.close()


# Fetch Live Jobs Function (Simulating nationwide expansion)
def fetch_and_add_live_jobs():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  new_jobs = [
      (
          "RRB NTPC Graduate & Undergrad",
          "Railway Recruitment Board",
          "12th / Graduate",
          "All India",
          "Sarkari",
          "RRB",
          "Multiple States",
      ),
      (
          "Python Django Developer",
          "Startup Inc",
          "B.Tech",
          "Maharashtra",
          "Private",
          "Wellfound",
          "Pune",
      ),
      (
          "Customer Support Executive",
          "Genpact",
          "Graduate",
          "Uttar Pradesh",
          "Private",
          "Naukri",
          "Noida",
      ),
      (
          "Bihar Police Constable Recruitment",
          "CSBC Bihar",
          "12th Pass",
          "Bihar",
          "Sarkari",
          "CSBC",
          "Patna, Bihar",
      ),
  ]

  added_count = 0
  for job in new_jobs:
    # Check duplicate
    cursor.execute(
        "SELECT COUNT(*) FROM jobs WHERE job_title = ? AND state = ?",
        (job[0], job[3]),
    )
    if cursor.fetchone()[0] == 0:
      cursor.execute(
          """
                INSERT INTO jobs (job_title, company, qualification, state, job_type, source, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
          job,
      )
      added_count += 1

  conn.commit()
  conn.close()
  return added_count


# Initialize DB on load
init_db()

# --- UI Layout ---
st.title("🇮🇳 All-India Job Aggregator Dashboard (Sarkari & Private)")
st.markdown(
    "Find small-to-large scale **Sarkari** and **Private** jobs spanning across"
    " all states and union territories of India."
)

# Sidebar for controls and filters
st.sidebar.header("🔍 Filters & Controls")

if st.sidebar.button("🔄 Fetch & Update Live Jobs"):
  count = fetch_and_add_live_jobs()
  st.sidebar.success(f"Successfully added {count} new pan-India jobs!")

# Filter by Job Type (Sarkari vs Private vs All)
job_type_filter = st.sidebar.radio(
    "Select Job Category:", ["All Jobs", "Sarkari", "Private"]
)

# Filter by State
selected_state = st.sidebar.selectbox("Select State / UT:", INDIAN_STATES)

# Load data from SQLite
conn = sqlite3.connect(DB_PATH)
query = "SELECT * FROM jobs"
df = pd.read_sql(query, conn)
conn.close()

# Apply Filters
if job_type_filter != "All Jobs":
  df = df[df["job_type"] == job_type_filter]

if selected_state != "All India":
  df = df[df["state"] == selected_state]

# Main Search Bar
search_query = st.text_input(
    "🔍 Search by Job Title, Company, Qualification, or Location:"
)
if search_query:
  df = df[
      df["job_title"].str.contains(search_query, case=False, na=False)
      | df["company"].str.contains(search_query, case=False, na=False)
      | df["qualification"].str.contains(search_query, case=False, na=False)
      | df["location"].str.contains(search_query, case=False, na=False)
  ]

# Display Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Jobs Found", len(df))
col2.metric(
    "Sarkari Jobs", len(df[df["job_type"] == "Sarkari"]) if not df.empty else 0
)
col3.metric(
    "Private Jobs", len(df[df["job_type"] == "Private"]) if not df.empty else 0
)

st.markdown("---")

# Display Table
if not df.empty:
  st.dataframe(
      df[
          [
              "job_title",
              "company",
              "qualification",
              "state",
              "job_type",
              "location",
              "source",
          ]
      ],
      use_container_width=True,
  )
else:
  st.warning(
      "No jobs found matching your filters. Try selecting 'All India' or 'All"
      " Jobs'."
)
    
