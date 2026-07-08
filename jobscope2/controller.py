from scraper.naukri_scraper import scrape_naukri
from scraper.foundit_scraper import scrape_foundit
from src.data_cleaning import clean_jobs
from src.analyzer import analyze_jobs

def get_jobs(keyword, location):
    """
    Main controller function
    """
    naukri_jobs = scrape_naukri(keyword, location)
    foundit_jobs = scrape_foundit(keyword, location)

    all_jobs = naukri_jobs + foundit_jobs

    # Clean data
    cleaned_jobs = clean_jobs(all_jobs)

    # Analyze data
    analysis = analyze_jobs(cleaned_jobs)

    return cleaned_jobs, analysis