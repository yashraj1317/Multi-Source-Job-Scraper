import re
import time
import random
from playwright.sync_api import sync_playwright


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def get_text(card, selector):
    try:
        return card.locator(selector).first.inner_text(timeout=2000).strip()
    except Exception:
        return ""


def get_apply_link(card):
    try:
        link = card.locator("a.title").first.get_attribute("href")
        if link:
            return link
    except Exception:
        pass

    try:
        link = card.locator("a").first.get_attribute("href")
        if link:
            return link
    except Exception:
        pass

    return ""


def scrape_naukri(role, location, limit=50, max_pages=6):
    jobs = []
    role_slug = slugify(role) if role else "jobs"
    loc_slug = slugify(location) if location else ""

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=300
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )

        page = context.new_page()

        for page_no in range(1, max_pages + 1):
            if len(jobs) >= limit:
                break

            if loc_slug:
                url = f"https://www.naukri.com/{role_slug}-jobs-in-{loc_slug}-{page_no}"
            else:
                url = f"https://www.naukri.com/{role_slug}-jobs-{page_no}"

            print(f"\nOpening page {page_no}: {url}")

            try:
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                page.wait_for_timeout(
                    random.randint(7000, 12000)
                )

                print("Current URL:", page.url)

                cards = page.locator(".srp-jobtuple-wrapper")
                count = cards.count()

                print("Found jobs:", count)

                if count == 0:
                    print("No jobs found. Stopping this cycle.")
                    break

                for i in range(count):
                    if len(jobs) >= limit:
                        break

                    card = cards.nth(i)

                    title = get_text(card, ".title")
                    company = get_text(card, ".comp-name")
                    experience = get_text(card, ".exp-wrap")
                    job_location = get_text(card, ".locWdth")
                    salary = get_text(card, ".sal-wrap")
                    skills = get_text(card, ".tags-gt")
                    apply_link = get_apply_link(card)

                    if title:
                        jobs.append({
                            "title": title,
                            "company": company,
                            "experience": experience,
                            "location": job_location,
                            "salary": salary,
                            "skills": skills,
                            "apply_link": apply_link,
                            "source": "Naukri"
                        })

                wait_time = random.randint(10, 20)
                print(f"Waiting {wait_time} seconds before next page...")
                time.sleep(wait_time)

            except Exception as e:
                print("Page error:", e)
                print("Skipping this page safely...")
                time.sleep(random.randint(5, 10))

        browser.close()

    return jobs[:limit]