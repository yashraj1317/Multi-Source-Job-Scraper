def analyze_jobs(jobs):
    """
    Perform basic analysis on job listings
    """
    analysis = {
        "total_jobs": len(jobs),
        "companies": {},
        "locations": {}
    }

    for job in jobs:
        company = job.get("company", "Unknown")
        location = job.get("location", "Unknown")

        # Count companies
        if company in analysis["companies"]:
            analysis["companies"][company] += 1
        else:
            analysis["companies"][company] = 1

        # Count locations
        if location in analysis["locations"]:
            analysis["locations"][location] += 1
        else:
            analysis["locations"][location] = 1

    return analysis