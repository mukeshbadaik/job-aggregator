import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime, date

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

# Initialize Database Schemas
def init_cloud_db():
    try:
        conn = get_cloud_connection()
        cur = conn.cursor()
        # Jobs Table
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
                job_type TEXT DEFAULT 'Private'
            );
        """)
        # Applications Table for In-App Apply
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id SERIAL PRIMARY KEY,
                job_id INT,
                job_title TEXT,
                applicant_name TEXT,
                applicant_email TEXT,
                phone_number TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Database Connection Error: {e}")

init_cloud_db()

# Insert Single Real Job to DB
def insert_real_job(title, company, sector, state, qual, salary, start_date, last_date, openings, job_type):
    try:
        conn = get_cloud_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO jobs (title, company, sector, state, qualification, salary, start_date, last_date, total_openings, job_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, company, sector, state, qual, salary, start_date, last_date, openings, job_type))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return False

# Save Application to DB
def submit_application(job_id, job_title, name, email, phone):
    try:
        conn = get_cloud_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO job_applications (job_id, job_title, applicant_name, applicant_email, phone_number)
            VALUES (%s, %s, %s, %s, %s)
        """, (job_id, job_title, name, email, phone))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return False

# Professional UI Layout
st.title("💼 Pan-India Unified Career Portal")
st.markdown("Real Sarkaari and Private Sector Vacancies with Direct In-App Application Support.")
st.markdown("---")

# Sidebar Admin Panel for Real Job Postings
st.sidebar.header("🛠️ Admin Panel (Post Real Job)")
with st.sidebar.form("admin_job_form"):
    st.markdown("### Add Real Vacancy")
    r_title = st.text_input("Job Title / Role")
    r_company = st.text_input("Company / Department Name")
    r_job_type = st.selectbox("Job Type", ["Government", "Private"])
    r_sector = st.text_input("Sector (e.g., Banking, IT, Railways)")
    r_state = st.selectbox("State / Location", ["Pan-India", "Maharashtra", "Karnataka", "Delhi NCR", "Uttar Pradesh", "Tamil Nadu", "Odisha", "Other"])
    r_qual = st.selectbox("Eligibility / Qualification", ["10th / 12th Pass", "ITI / Diploma", "B.Tech / B.E.", "MBA / PGDM", "Any Graduate"])
    r_salary = st.text_input("Salary / Pay Scale (e.g., 6 LPA or Level 7)")
    r_start = st.date_input("Start Date", value=date.today())
    r_last = st.date_input("Last Date to Apply", value=date.today())
    r_openings = st.number_input("Total Openings", min_value=1, value=10)
    
    submitted_job = st.form_submit_button("Publish Real Job")
    if submitted_job:
        if r_title and r_company:
            success = insert_real_job(r_title, r_company, r_sector, r_state, r_qual, r_salary, r_start, r_last, r_openings, r_job_type)
            if success:
                st.sidebar.success("Real vacancy published successfully!")
                st.rerun()
            else:
                st.sidebar.error("Failed to publish job.")
        else:
            st.sidebar.warning("Please enter Job Title and Company.")

# Fetch Jobs Data
@st.cache_data(ttl=10)
def fetch_jobs():
    try:
        conn = get_cloud_connection()
        query = "SELECT id, title, company, sector, state, qualification, salary, start_date, last_date, total_openings, job_type FROM jobs ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

df_jobs = fetch_jobs()

if not df_jobs.empty:
    tab_govt, tab_private = st.tabs(["🏛️ Sarkaari Jobs (Government)", "💼 Private Jobs"])

    # --- GOVT JOBS TAB ---
    with tab_govt:
        st.subheader("Government & PSU Sector Vacancies")
        govt_df = df_jobs[df_jobs["job_type"] == "Government"]
        
        if not govt_df.empty:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                g_state = st.selectbox("Filter State (Govt)", ["All"] + list(govt_df["state"].dropna().unique()), key="g_state")
            with col_f2:
                g_qual = st.selectbox("Filter Qualification (Govt)", ["All"] + list(govt_df["qualification"].dropna().unique()), key="g_qual")
            
            if g_state != "All":
                govt_df = govt_df[govt_df["state"] == g_state]
            if g_qual != "All":
                govt_df = govt_df[govt_df["qualification"] == g_qual]

            st.write(f"Found **{len(govt_df)}** Sarkaari vacancies")
            
            for index, row in govt_df.iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"### **{row['title']}**")
                        st.write(f"🏢 **Department:** {row['company']} | 🏷️ **Sector:** {row['sector']}")
                        st.write(f"📍 **State:** {row['state']} | 🎓 **Eligibility:** {row['qualification']}")
                    with c2:
                        st.write(f"💰 **Pay Scale:** {row['salary']}")
                        st.write(f"📅 **Last Date:** {row['last_date']} | 👥 **Openings:** {row['total_openings']}")
                    with c3:
                        if st.button("Apply Now", key=f"govt_btn_{row['id']}"):
                            st.session_state[f"form_open_{row['id']}"] = True

                    if st.session_state.get(f"form_open_{row['id']}", False):
                        with st.form(key=f"govt_form_{row['id']}"):
                            st.markdown(f"#### Sarkaari Application: {row['title']} ({row['company']})")
                            aname = st.text_input("Full Name", key=f"gn_{row['id']}")
                            aemail = st.text_input("Email Address", key=f"ge_{row['id']}")
                            aphone = st.text_input("Phone Number", key=f"gp_{row['id']}")
                            res = st.file_uploader("Upload Resume/Documents (PDF)", type=["pdf", "docx"], key=f"gr_{row['id']}")
                            
                            if st.form_submit_button("Submit Sarkaari Application"):
                                if aname and aemail and aphone:
                                    if submit_application(row['id'], row['title'], aname, aemail, aphone):
                                        st.success("🎉 Sarkaari application submitted successfully!")
                                        st.session_state[f"form_open_{row['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error("Submission failed. Try again.")
                                else:
                                    st.warning("Please fill all fields.")
                    st.markdown("---")
        else:
            st.info("No government jobs available right now. Use the sidebar admin panel to post real government vacancies.")

    # --- PRIVATE JOBS TAB ---
    with tab_private:
        st.subheader("Private Sector Vacancies")
        priv_df = df_jobs[df_jobs["job_type"] == "Private"]
        
        if not priv_df.empty:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                p_state = st.selectbox("Filter State (Private)", ["All"] + list(priv_df["state"].dropna().unique()), key="p_state")
            with col_p2:
                p_qual = st.selectbox("Filter Qualification (Private)", ["All"] + list(priv_df["qualification"].dropna().unique()), key="p_qual")
            
            if p_state != "All":
                priv_df = priv_df[priv_df["state"] == p_state]
            if p_qual != "All":
                priv_df = priv_df[priv_df["qualification"] == p_qual]

            st.write(f"Found **{len(priv_df)}** Private vacancies")
            
            for index, row in priv_df.iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"### **{row['title']}**")
                        st.write(f"🏢 **Company:** {row['company']} | 🏷️ **Sector:** {row['sector']}")
                        st.write(f"📍 **State:** {row['state']} | 🎓 **Eligibility:** {row['qualification']}")
                    with c2:
                        st.write(f"💰 **Salary:** {row['salary']}")
                        st.write(f"📅 **Last Date:** {row['last_date']} | 👥 **Openings:** {row['total_openings']}")
                    with c3:
                        if st.button("Apply Now", key=f"priv_btn_{row['id']}"):
                            st.session_state[f"form_open_{row['id']}"] = True

                    if st.session_state.get(f"form_open_{row['id']}", False):
                        with st.form(key=f"priv_form_{row['id']}"):
                            st.markdown(f"#### Private Application: {row['title']} at {row['company']}")
                            aname = st.text_input("Full Name", key=f"pn_{row['id']}")
                            aemail = st.text_input("Email Address", key=f"pe_{row['id']}")
                            aphone = st.text_input("Phone Number", key=f"pp_{row['id']}")
                            res = st.file_uploader("Upload Resume (PDF)", type=["pdf", "docx"], key=f"pr_{row['id']}")
                            
                            if st.form_submit_button("Submit Private Application"):
                                if aname and aemail and aphone:
                                    if submit_application(row['id'], row['title'], aname, aemail, aphone):
                                        st.success("🎉 Private application submitted successfully!")
                                        st.session_state[f"form_open_{row['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error("Submission failed. Try again.")
                                else:
                                    st.warning("Please fill all fields.")
                    st.markdown("---")
        else:
            st.info("No private jobs available right now. Use the sidebar admin panel to post real private vacancies.")
else:
    st.info("Database is currently empty. Use the sidebar **'Admin Panel'** to add real government or private job vacancies.")
        
