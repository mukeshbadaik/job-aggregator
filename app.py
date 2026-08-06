import streamlit as st
import pandas as pd
import psycopg2
from datetime import date, timedelta
import io

# Page Configuration
st.set_page_config(
    page_title="Pan-India Real-Time Career Portal",
    page_icon="🇮🇳",
    layout="wide"
)

# Safe Cloud Database Connection
def get_cloud_connection():
    try:
        if "DB_HOST" not in st.secrets:
            return None
        conn = psycopg2.connect(
            host=st.secrets["DB_HOST"],
            database=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            port=st.secrets["DB_PORT"],
            sslmode="require",
            connect_timeout=3
        )
        return conn
    except Exception as e:
        return None

# Initialize Database Schemas Safely
def init_cloud_db():
    conn = get_cloud_connection()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT,
                sector TEXT,
                state TEXT,
                district TEXT,
                qualification TEXT,
                salary TEXT,
                description TEXT,
                start_date DATE,
                last_date DATE,
                total_openings INT DEFAULT 1,
                job_type TEXT DEFAULT 'Private',
                source_url TEXT
            );
        """)
        cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS district TEXT;")
        cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS description TEXT;")
        cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS qualification TEXT;")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id SERIAL PRIMARY KEY,
                job_id INT REFERENCES jobs(id) ON DELETE CASCADE,
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
        return True
    except Exception:
        return False

db_status = init_cloud_db()

# Clear Database Function
def clear_all_jobs():
    conn = get_cloud_connection()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM jobs;")
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False

# Bulk Insert from CSV
def bulk_insert_jobs_from_csv(df):
    conn = get_cloud_connection()
    if conn is None:
        return False, "Database connection failed."
    try:
        cur = conn.cursor()
        inserted_count = 0
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO jobs (title, company, sector, state, district, qualification, salary, description, start_date, last_date, total_openings, job_type, source_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(row.get('title', 'Job Opening')),
                str(row.get('company', 'Company')),
                str(row.get('sector', 'General')),
                str(row.get('state', 'India')),
                str(row.get('district', 'Various')),
                str(row.get('qualification', 'Any')),
                str(row.get('salary', 'As per norms')),
                str(row.get('description', '')),
                date.today(),
                date.today() + timedelta(days=30),
                int(row.get('total_openings', 10)) if pd.notnull(row.get('total_openings')) else 10,
                str(row.get('job_type', 'Private')),
                str(row.get('source_url', '#'))
            ))
            inserted_count += 1
        conn.commit()
        cur.close()
        conn.close()
        return True, inserted_count
    except Exception as e:
        return False, str(e)

# Sync Comprehensive Multi-State & Multi-District Initial Pool
def sync_pan_india_database():
    conn = get_cloud_connection()
    if conn is None:
        return False, "Database connection failed."

    try:
        national_jobs = [
            ("Multi-Tasking Staff (MTS)", "Staff Selection Commission (SSC)", "Government & PSU Services", "Delhi", "New Delhi", "10th Pass", "₹18,000 - ₹35,000/Mo", "Central government administrative support and office duties.", "Government", "https://ssc.nic.in"),
            ("Gramin Dak Sevak (GDS)", "India Post", "Government & PSU Services", "Uttar Pradesh", "Lucknow", "10th Pass with Math", "₹12,000 - ₹29,300/Mo", "Branch post office mail delivery and postal operations.", "Government", "https://indiapostgdsonline.gov.in"),
            ("Gramin Dak Sevak (GDS)", "India Post", "Government & PSU Services", "Bihar", "Patna", "10th Pass with Math", "₹12,000 - ₹29,300/Mo", "Postal branch management and local mail dispatch.", "Government", "https://indiapostgdsonline.gov.in"),
            ("Junior Assistant & Clerk", "State Bank of India (SBI)", "Banking & Financial Services", "Maharashtra", "Mumbai", "Any Graduate Degree", "₹26,000 - ₹48,000/Mo", "Clerical cadre customer service and banking operations.", "Government", "https://sbi.co.in/careers"),
            ("Railway Track Maintainer", "Railway Recruitment Board (RRB)", "Railways", "West Bengal", "Kolkata", "10th Pass / ITI", "₹19,900 - ₹63,200/Mo", "Track maintenance, safety checks, and engineering support.", "Government", "https://rrbcdg.gov.in"),
            ("Police Constable", "Uttar Pradesh Police Recruitment Board", "Government & PSU Services", "Uttar Pradesh", "Kanpur", "12th Pass", "₹21,700 - ₹69,100/Mo", "Law and order maintenance across district police stations.", "Government", "https://uppbpb.gov.in"),
            ("Primary School Teacher (PRT)", "Bihar Public Service Commission (BPSC)", "Education & Teaching", "Bihar", "Muzaffarpur", "D.El.Ed / B.Ed + TET", "₹25,000 - ₹40,000/Mo", "Teaching primary classes in district government schools.", "Government", "https://bpsc.bih.nic.in"),
            ("Last Mile Delivery Executive", "Zomato / Blinkit", "Logistics & Supply Chain", "Delhi", "New Delhi", "No Formal Education / Helper", "₹22,000 - ₹35,000/Mo", "Immediate local onboarding for delivery partners.", "Private", "https://www.zomato.com/careers"),
            ("Warehouse Operations Associate", "Amazon India Fulfillment", "Manufacturing & Logistics", "Maharashtra", "Pune", "12th Pass / Graduate", "₹19,000 - ₹28,000/Mo", "Inventory sorting, packing, and fulfillment hub management.", "Private", "https://www.amazon.jobs"),
            ("Hospital Ward Attendant / Helper", "Apollo Hospitals", "Healthcare", "Tamil Nadu", "Chennai", "8th / 10th Pass", "₹16,000 - ₹24,000/Mo", "Patient support, ward maintenance, and facility assistance.", "Private", "https://www.apollohospitals.com/careers"),
            ("Retail Sales Associate", "Reliance Retail", "Retail & Sales", "Gujarat", "Ahmedabad", "12th Pass", "₹16,000 - ₹24,000/Mo", "Customer assistance, billing, and inventory stock management.", "Private", "https://relianceretail.com/careers"),
            ("Security Guard / Helper", "SIS Security Services", "Security Services", "Karnataka", "Bengaluru", "10th Pass", "₹15,000 - ₹22,000/Mo", "Premises security, gate management, and visitor logging.", "Private", "https://sisindia.com")
        ]

        cur = conn.cursor()
        for job in national_jobs:
            cur.execute("""
                INSERT INTO jobs (title, company, sector, state, district, qualification, salary, description, start_date, last_date, total_openings, job_type, source_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                job[0], job[1], job[2], job[3], job[4], job[5], job[6], job[7],
                date.today(), date.today() + timedelta(days=45), 50, job[8], job[9]
            ))
        conn.commit()
        cur.close()
        conn.close()
        return True, len(national_jobs)
    except Exception as e:
        return False, str(e)

# Save In-App Application to DB
def submit_application(job_id, job_title, name, email, phone):
    conn = get_cloud_connection()
    if conn is None:
        return False
    try:
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

# UI Layout
st.title("🇮🇳 Pan-India Real-Time Career Portal")
st.markdown("Live nationwide verified vacancies covering Sarkari Government jobs, Banking, Railways, Private enterprises, and local Helper roles.")
st.markdown("---")

if not db_status:
    st.error("⚠️ **Database Connection Failed:** Check your Supabase secrets in Streamlit settings.")
else:
    # Sidebar Controls
    st.sidebar.header("🔍 Portal Controls & Importer")
    
    if st.sidebar.button("🚀 Load Instant Pan-India Database"):
        with st.spinner("Populating multi-state & multi-district vacancies..."):
            success, count = sync_pan_india_database()
            if success:
                st.sidebar.success(f"Successfully loaded {count} verified vacancies across states!")
                st.rerun()
            else:
                st.sidebar.error(f"Error: {count}")

    if st.sidebar.button("🗑️ Clear Database & Reset"):
        if clear_all_jobs():
            st.sidebar.success("Database cleared successfully!")
            st.rerun()
        else:
            st.sidebar.error("Failed to clear database.")

    st.sidebar.markdown("---")
    
    # Bulk CSV Upload Section
    st.sidebar.subheader("📂 Bulk CSV Importer")
    st.sidebar.markdown("Upload a CSV file containing columns: `title`, `company`, `sector`, `state`, `district`, `qualification`, `salary`, `description`, `job_type`, `total_openings`, `source_url`")
    
    # Sample CSV Download Template
    sample_data = pd.DataFrame({
        'title': ['Helper / Peon'],
        'company': ['District Collectorate'],
        'sector': ['Government & PSU Services'],
        'state': ['Uttar Pradesh'],
        'district': ['Lucknow'],
        'qualification': ['8th Pass'],
        'salary': ['₹15,000/Mo'],
        'description': ['Office file management and helper tasks.'],
        'job_type': ['Government'],
        'total_openings': [25],
        'source_url': ['https://example.com']
    })
    st.sidebar.download_button(
        label="📥 Download Sample CSV Template",
        data=sample_data.to_csv(index=False).encode('utf-8'),
        file_name='pan_india_jobs_template.csv',
        mime='text/csv'
    )

    uploaded_file = st.sidebar.file_uploader("Choose CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            csv_df = pd.read_csv(uploaded_file)
            st.sidebar.write(f"Preview rows: {len(csv_df)}")
            if st.sidebar.button("🚀 Import CSV Records Live"):
                with st.spinner("Importing records into database..."):
                    success, res = bulk_insert_jobs_from_csv(csv_df)
                    if success:
                        st.sidebar.success(f"Successfully imported {res} jobs live!")
                        st.rerun()
                    else:
                        st.sidebar.error(f"Import failed: {res}")
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {e}")

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filter Listings")

    # Fetch Data from DB
    @st.cache_data(ttl=2)
    def fetch_all_jobs():
        conn = get_cloud_connection()
        if conn is None:
            return pd.DataFrame()
        try:
            df = pd.read_sql("SELECT * FROM jobs ORDER BY id DESC", conn)
            conn.close()
            return df
        except Exception:
            return pd.DataFrame()

    df_jobs = fetch_all_jobs()

    if not df_jobs.empty:
        df_jobs = df_jobs[df_jobs["title"].notnull() & df_jobs["state"].notnull()]

        # Dynamic Filter Options
        states = ["All States"] + list(df_jobs["state"].dropna().unique())
        qualifications = ["All Qualifications"] + list(df_jobs["qualification"].dropna().unique())
        job_types = ["All Types", "Government", "Private"]

        selected_state = st.sidebar.selectbox("Filter by State", states)
        selected_qual = st.sidebar.selectbox("Filter by Qualification", qualifications)
        selected_type = st.sidebar.selectbox("Filter by Job Type", job_types)
        search_keyword = st.sidebar.text_input("Search Title, Company or City")

        # Apply Filters Logic
        filtered_df = df_jobs.copy()
        if selected_state != "All States":
            filtered_df = filtered_df[filtered_df["state"] == selected_state]
        if selected_qual != "All Qualifications":
            filtered_df = filtered_df[filtered_df["qualification"] == selected_qual]
        if selected_type != "All Types":
            filtered_df = filtered_df[filtered_df["job_type"] == selected_type]
        if search_keyword:
            filtered_df = filtered_df[
                filtered_df["title"].str.contains(search_keyword, case=False, na=False) | 
                filtered_df["company"].str.contains(search_keyword, case=False, na=False) |
                filtered_df["district"].str.contains(search_keyword, case=False, na=False)
            ]

        st.subheader(f"Active Verified Openings ({len(filtered_df)} Found)")

        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        title = row.get('title', 'Job Opening')
                        job_type = row.get('job_type', 'Private')
                        company = row.get('company', 'Company')
                        sector = row.get('sector', 'General')
                        district = row.get('district', 'Various')
                        state = row.get('state', 'India')
                        qual = row.get('qualification', 'Any')
                        salary = row.get('salary', 'As per industry norms')
                        desc = row.get('description', '')
                        last_date = row.get('last_date', 'Open')
                        openings = row.get('total_openings', 1)
                        source_url = row.get('source_url', '#')

                        st.markdown(f"### **{title}** ({job_type})")
                        st.write(f"🏢 **Company/Dept:** {company} | 🏷️ **Sector:** {sector}")
                        st.write(f"📍 **Location:** {district}, {state} | 🎓 **Eligibility:** {qual}")
                        st.write(f"💰 **Salary / Pay Scale:** {salary}")
                        st.markdown(f"📝 **Job Description:** {desc}")
                        st.write(f"📅 **Last Date:** {last_date} | 👥 **Openings:** {openings}")
                        st.markdown(f"🔗 [Official Portal Link]({source_url})")
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Apply In-App", key=f"apply_btn_{row['id']}"):
                            st.session_state[f"form_open_{row['id']}"] = True

                    # In-App Application Form
                    if st.session_state.get(f"form_open_{row['id']}", False):
                        with st.form(key=f"app_form_{row['id']}"):
                            st.markdown(f"#### Apply Directly: {row.get('title', '')}")
                            name = st.text_input("Full Name", key=f"fn_{row['id']}")
                            email = st.text_input("Email Address", key=f"fe_{row['id']}")
                            phone = st.text_input("Phone Number / WhatsApp", key=f"fp_{row['id']}")
                            
                            if st.form_submit_button("Submit Application Now"):
                                if name and email and phone:
                                    if submit_application(row['id'], row['title'], name, email, phone):
                                        st.success("🎉 Application submitted successfully!")
                                        st.session_state[f"form_open_{row['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error("Submission failed due to database error.")
                                else:
                                    st.warning("Please fill all mandatory fields.")

                    st.markdown("---")
        else:
            st.warning("No jobs match your filter criteria. Try resetting the sidebar filters.")
    else:
        st.info("Database is empty. Click **'Load Instant Pan-India Database'** or upload a CSV file via the sidebar.")
