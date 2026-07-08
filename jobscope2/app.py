import streamlit as st

from scraper.naukri_scraper import scrape_naukri
from scraper.foundit_scraper import scrape_foundit

st.set_page_config(page_title="JobScope", layout="wide")


# ✅ SESSION STATE
if "all_jobs" not in st.session_state:
    st.session_state.all_jobs = []


# ✅ SIDEBAR
with st.sidebar:
    st.header("Job Filters")

    role = st.text_input("Job Role")
    location = st.text_input("Location")

    search_clicked = st.button("Search")


# ✅ MAIN UI
st.title("JobScope")
st.write("Live Job Recommendation Website")


# ✅ SEARCH LOGIC
if search_clicked:
    if not role:
        st.warning("Please enter a job role.")
    else:
        with st.spinner("Scraping Naukri..."):
            naukri_jobs = scrape_naukri(role, location, limit=50)

        with st.spinner("Scraping Foundit..."):
            foundit_jobs = scrape_foundit(role, location, limit=50)

        st.session_state.all_jobs = naukri_jobs + foundit_jobs


# ✅ DISPLAY RESULTS
all_jobs = st.session_state.all_jobs

if all_jobs:
    naukri_count = len([j for j in all_jobs if j.get("source") == "Naukri"])
    foundit_count = len([j for j in all_jobs if j.get("source") == "Foundit"])

    st.subheader(f"Total Jobs Found: {len(all_jobs)}")
    st.write(f"Naukri: {naukri_count}  |  Foundit: {foundit_count}")

    st.write("---")

    # ✅ JOB DISPLAY
    for job in all_jobs:
        st.markdown(f"### {job.get('title', '')}")
        st.write(f"**Company:** {job.get('company', '')}")
        st.write(f"**Location:** {job.get('location', '')}")
        st.write(f"**Experience:** {job.get('experience', '')}")
        st.write(f"**Salary:** {job.get('salary', '')}")
        st.write(f"**Skills:** {job.get('skills', '')}")
        st.write(f"**Source:** {job.get('source', '')}")

        if job.get("apply_link"):
            st.write(f"[Apply Now]({job.get('apply_link')})")

        st.write("---")

else:
    st.info("Enter a job role and location in the sidebar, then click Search.")