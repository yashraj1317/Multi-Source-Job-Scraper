import re
import time
import random
from playwright.sync_api import sync_playwright


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def full_link(link):
    if not link:
        return ""
    if link.startswith("/"):
        return "https://www.foundit.in" + link
    return link


def is_real_job_link(href):
    if "foundit.in" not in href:
        return False
    if "/job/" not in href:
        return False
    if "/search/" in href:
        return False
    if "jobs-career" in href:
        return False
    return True


CARD_TEXT_JS = """
el => {
    let cur = el;
    for (let i = 0; i < 6; i++) {
        cur = cur.parentElement;
        if (!cur) break;
        if (cur.innerText && cur.innerText.length > 80) {
            return cur.innerText;
        }
    }
    return el.innerText;
}
"""


def parse_card_text(text, apply_link):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return None

    title = lines[0]
    company = lines[1] if len(lines) > 1 else ""

    experience = ""
    location = ""
    skills = ""
    salary = ""

    exp_pattern = re.compile(r"(\d+\s*-\s*\d+\s*yrs|\bFresher\b|\d+\+?\s*yrs)", re.IGNORECASE)
    loc_pattern = re.compile(r"^[A-Za-z\.\s]+,\s*[A-Za-z\s]+$")
    salary_pattern = re.compile(r"(₹|LPA|Not disclosed)", re.IGNORECASE)

    for line in lines:
        if not experience and exp_pattern.search(line):
            experience = exp_pattern.search(line).group(0)
        if not location and loc_pattern.match(line) and "skills" not in line.lower():
            location = line
        if line.lower().startswith("skills"):
            skills = line.split(":", 1)[-1].strip()
        if not salary and salary_pattern.search(line):
            salary = line

    if not title or title.strip().lower() in ("jobs", ""):
        return None

    return {
        "title": title,
        "company": company,
        "experience": experience,
        "location": location,
        "salary": salary,
        "skills": skills,
        "apply_link": apply_link,
        "source": "Foundit"
    }


def scrape_foundit(role, location, limit=50, max_pages=6):
    jobs = []
    seen_links = set()
    query = role.strip() if role else ""
    loc = location.strip() if location else "india"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )

        page = context.new_page()

        for page_no in range(1, max_pages + 1):
            if len(jobs) >= limit:
                break

            url = (
                f"https://www.foundit.in/search/jobs?"
                f"query={query.replace(' ', '%20')}"
                f"&locations={loc.replace(' ', '%20')}"
                f"&limit=20&page={page_no}"
            )

            print(f"\nOpening Foundit page {page_no}: {url}")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(random.randint(6000, 9000))

                print("Current URL:", page.url)

                link_elements = page.locator("a")
                count = link_elements.count()

                page_jobs_found = 0

                for i in range(count):
                    if len(jobs) >= limit:
                        break

                    try:
                        anchor = link_elements.nth(i)
                        href = anchor.get_attribute("href")
                        href = full_link(href)

                        if not href or not is_real_job_link(href):
                            continue
                        if href in seen_links:
                            continue

                        card_text = anchor.evaluate(CARD_TEXT_JS)
                        job = parse_card_text(card_text, href)

                        if job:
                            seen_links.add(href)
                            jobs.append(job)
                            page_jobs_found += 1
                            print("Saved:", job["title"])

                    except Exception:
                        continue

                print(f"Page {page_no}: {page_jobs_found} jobs parsed from listing")

                if page_jobs_found == 0:
                    print("No jobs parsed on this page. Stopping.")
                    break

                wait_time = random.randint(4, 7)
                print(f"Waiting {wait_time} seconds before next page...")
                time.sleep(wait_time)

            except Exception as e:
                print("Page error:", e)
                time.sleep(random.randint(3, 6))

        browser.close()

    return jobs[:limit]