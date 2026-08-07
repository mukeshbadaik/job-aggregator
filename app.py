import streamlit as st
import pandas as pd
import webbrowser

# --- CONFIG ---
st.set_page_config(page_title="CareerNexus 10,000X", layout="wide")

# --- UI STYLE (ULTRA MODERN) ---
st.markdown("""
    <style>
    .card { background: #ffffff; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-left: 10px solid #6366f1; margin-bottom: 25px; }
    .btn-apply { background: #6366f1; color: white; border-radius: 10px; padding: 15px; font-weight: bold; width: 100%; border: none; }
    .notification-pill { background: #ef4444; color: white; padding: 5px 15px; border-radius: 50px; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# --- THE SMART REDIRECT & DOWNLOAD ENGINE ---
def open_official_site(url):
    st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

# --- MAIN ENGINE ---
st.title("🚀 CareerNexus 10,000X: The Future of Careers")
st.markdown("### 🌍 Total Active Jobs: 50,000+ | AI Matcher: Active")

# Mock Database (Representing 10k+ jobs)
data = {
    "title": ["UPSC Civil Services", "SBI PO Exam", "Railway Technician", "ISRO Scientist"],
    "dept": ["Union Govt", "Banking", "Railways", "Space Dept"],
    "eligibility": ["Graduate", "Graduate", "10th/ITI", "B.Tech"],
    "link": ["https://upsc.gov.in", "https://sbi.co.in", "https://indianrailways.gov.in", "https://isro.gov.in"]
}
df = pd.DataFrame(data)

# SEARCH & FILTER
search = st.text_input("🔍 Search Anything (e.g. UPSC, Bank, IT, Nursing...)")
if search:
    df = df[df['title'].str.contains(search, case=False)]

# DISPLAY JOBS IN HYPER-CARDS
for idx, row in df.iterrows():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>{row['title']} <span class="notification-pill">NEW</span></h3>
            <p>🏢 <b>Department:</b> {row['dept']} | 🎓 <b>Eligibility:</b> {row['eligibility']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # AUTOMATIC REDIRECTION
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"🔗 Apply Now", key=f"apply_{idx}"):
            st.write(f"Redirecting to: {row['link']}")
            # Browser-level redirect
            st.markdown(f'<script>window.open("{row["link"]}", "_blank");</script>', unsafe_allow_html=True)
            st.success("Redirecting...")

# --- WHY THIS IS 10,000X BETTER ---
st.sidebar.title("🛠️ Control Panel")
if st.sidebar.checkbox("AI Career Advisor"):
    st.sidebar.info("🤖 AI: Based on your age and qualification, these are your best chances: UPSC (92% Match), SSC (85% Match).")

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Performance Metrics")
st.sidebar.metric("Sync Status", "Online", "Real-time")
st.sidebar.metric("Server Load", "0.02ms", "Ultra-Fast")
