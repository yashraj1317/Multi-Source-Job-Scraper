def clean_jobs(jobs):
    """
    Clean and standardize job data
    """
    cleaned = []

    seen = set()

    for job in jobs:
        title = job.get("title", "").strip()
        company = job.get("company", "").strip()
        location = job.get("location", "").strip()
        source = job.get("source", "").strip()

        # Remove duplicates
        key = (title.lower(), company.lower(), location.lower())
        if key in seen:
            continue
        seen.add(key)

        # Normalize text
        cleaned.append({
            "title": title.title(),
            "company": company.title(),
            "location": location.title(),
            "source": source
        })

    return cleaned