import time
import re
import random
import os
import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
JOB_DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.linkedin.com/jobs/search?location=Glasgow%2C%20United%20Kingdom",
    }

def scrape_jobs(title="", location="Glasgow, United Kingdom", max_jobs=200):
    jobs = []
    seen_job_ids = set()
    start = 0
    page_size = 25
    
    session = requests.Session()

    print(f"Starting job scrape for title: '{title}', location: '{location}' (Target max jobs: {max_jobs})...")

    while len(jobs) < max_jobs:
        params = {
            "location": location,
            "start": start
        }
        if title:
            params["keywords"] = title
        
        print(f"\nFetching search results page at start index {start}...")
        try:
            response = session.get(BASE_SEARCH_URL, headers=get_headers(), params=params, timeout=15)
            if response.status_code != 200:
                print(f"Failed to fetch search page (HTTP {response.status_code}). Stopping search pagination.")
                break
            
            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("li")
            
            if not job_cards:
                # Also try finding job cards directly if tags are different
                job_cards = soup.find_all("div", class_=re.compile(r"job-search-card|base-card"))
            
            if not job_cards:
                print("No more job cards found. Reached end of results.")
                break
                
            new_cards_count = 0
            for card in job_cards:
                if len(jobs) >= max_jobs:
                    break
                    
                # Extract Job ID & URL
                link_elem = card.find("a", class_=re.compile(r"base-card__full-link|job-search-card__link"))
                if not link_elem:
                    link_elem = card.find("a", href=True)
                
                if not link_elem or "href" not in link_elem.attrs:
                    continue
                
                raw_url = link_elem["href"].split("?")[0]
                
                # Extract job ID
                job_id = None
                id_match = re.search(r"-(\d+)$", raw_url) or re.search(r"/view/(\d+)", raw_url)
                if id_match:
                    job_id = id_match.group(1)
                else:
                    urn = card.find("div", {"data-entity-urn": True})
                    if urn:
                        job_id = urn["data-entity-urn"].split(":")[-1]
                
                if not job_id or job_id in seen_job_ids:
                    continue
                
                seen_job_ids.add(job_id)
                new_cards_count += 1

                # Extract Basic Information
                title_elem = card.find(class_=re.compile(r"title"))
                title = title_elem.get_text(strip=True) if title_elem else "N/A"

                company_elem = card.find(class_=re.compile(r"subtitle|company"))
                company = company_elem.get_text(strip=True) if company_elem else "N/A"

                loc_elem = card.find(class_=re.compile(r"location"))
                job_location = loc_elem.get_text(strip=True) if loc_elem else "N/A"

                time_elem = card.find("time")
                posted_date = time_elem.get_text(strip=True) if time_elem else "N/A"
                datetime_str = time_elem.get("datetime", "") if time_elem else ""

                job_info = {
                    "Job ID": job_id,
                    "Title": title,
                    "Company": company,
                    "Location": job_location,
                    "Posted Date": posted_date,
                    "Date Posted ISO": datetime_str,
                    "Job URL": raw_url,
                    "Description": "",
                    "Seniority Level": "",
                    "Employment Type": "",
                    "Job Function": "",
                    "Industries": ""
                }

                jobs.append(job_info)
                print(f"[{len(jobs)}] Found: {title} at {company} ({job_location})")

            if new_cards_count == 0:
                print("No new unique jobs on this page. Reached end.")
                break
                
            start += page_size
            time.sleep(random.uniform(1.0, 2.5)) # Polite delay

        except Exception as e:
            print(f"Error during search request: {e}")
            break

    print(f"\nSuccessfully collected metadata for {len(jobs)} jobs.")
    
    # Detailed fetch for descriptions & job criteria
    print("\nFetching full details and descriptions for each job...")
    for idx, job in enumerate(jobs, 1):
        job_id = job["Job ID"]
        detail_url = JOB_DETAIL_URL.format(job_id=job_id)
        print(f"[{idx}/{len(jobs)}] Fetching details for Job ID {job_id} ({job['Title']})...")
        
        try:
            res = session.get(detail_url, headers=get_headers(), timeout=10)
            if res.status_code == 200:
                dsoup = BeautifulSoup(res.text, "html.parser")
                
                # Job description
                desc_elem = dsoup.find("div", class_=re.compile(r"show-more-less-html__markup|description__text"))
                if desc_elem:
                    # Clean description text
                    job["Description"] = desc_elem.get_text(separator="\n", strip=True)
                
                # Job Criteria (Seniority level, Employment type, Job function, Industries)
                criteria_list = dsoup.find_all("li", class_=re.compile(r"description__job-criteria-item"))
                for item in criteria_list:
                    header = item.find(class_=re.compile(r"description__job-criteria-subheader"))
                    text = item.find(class_=re.compile(r"description__job-criteria-text"))
                    if header and text:
                        h_str = header.get_text(strip=True).lower()
                        t_str = text.get_text(strip=True)
                        if "seniority" in h_str:
                            job["Seniority Level"] = t_str
                        elif "employment" in h_str:
                            job["Employment Type"] = t_str
                        elif "function" in h_str:
                            job["Job Function"] = t_str
                        elif "industr" in h_str:
                            job["Industries"] = t_str

            time.sleep(random.uniform(0.5, 1.2)) # Polite delay between detail requests

        except Exception as e:
            print(f"  Warning: Failed to fetch detail for job {job_id}: {e}")

    return jobs

def save_to_excel_and_csv(jobs, output_prefix="LinkedIn_Jobs_Glasgow"):
    if not jobs:
        print("No jobs to save.")
        return None, None
        
    df = pd.DataFrame(jobs)
    
    excel_file = f"{output_prefix}.xlsx"
    csv_file = f"{output_prefix}.csv"
    
    # Save CSV
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"Saved CSV: {csv_file}")
    
    # Save Excel with formatting
    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="LinkedIn Jobs")
        worksheet = writer.sheets["LinkedIn Jobs"]
        
        # Adjust column widths & wrap description text
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            if col[0].value == "Description":
                worksheet.column_dimensions[col_letter].width = 50
            elif col[0].value in ["Job URL", "Job ID"]:
                worksheet.column_dimensions[col_letter].width = 35
            else:
                worksheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)
                
    print(f"Saved Excel: {os.path.abspath(excel_file)}")
    return excel_file, csv_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape LinkedIn jobs to Excel/CSV")
    parser.add_argument("--title", "-t", type=str, default="", help="Job title or keywords (e.g. 'Software Engineer')")
    parser.add_argument("--location", "-l", type=str, default="Glasgow, United Kingdom", help="Location (e.g. 'Glasgow')")
    parser.add_argument("--max-jobs", "-m", type=int, default=150, help="Max jobs to fetch")
    args = parser.parse_args()

    title_part = args.title.replace(' ', '_').lower() if args.title else 'all'
    loc_part = args.location.split(',')[0].replace(' ', '_').lower()
    file_prefix = f"LinkedIn_Jobs_{title_part}_{loc_part}"

    jobs_data = scrape_jobs(title=args.title, location=args.location, max_jobs=args.max_jobs)
    save_to_excel_and_csv(jobs_data, file_prefix)
