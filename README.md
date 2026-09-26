# 🎯 job_hunt — Open-Source Job Market Intelligence & Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![Open Source Love](https://img.shields.io/badge/Open%20Source-%E2%99%A5-rose.svg)]()

> A lightweight, ethical job search automation and market intelligence toolkit designed to democratize access to real-time hiring data. Extracts and structures full job descriptions, seniority levels, criteria, and employment details across international tech hubs into formatted Excel workbooks and CSV files.

---

## 💡 Why `job_hunt`?

In today's fast-moving job market, finding relevant job opportunities shouldn't require paying for enterprise data scrapers or manually checking dozens of search pages every day.

`job_hunt` was built to:
- **Empower Job Seekers & Career Changers**: Automate tedious manual searches and track new job openings matching exact target roles.
- **Enable Labour Market Research**: Provide workforce analysts and researchers with raw, structured hiring data (seniority levels, hiring industries, job functions).
- **Operate Lightweight & Headless**: Avoid resource-heavy browser drivers (Puppeteer/Selenium) by using lightweight HTTP session pooling, randomized user-agent rotation, and polite request backoffs.

---

## ✨ Features

- ⚡ **Lightweight & Fast**: Direct API endpoint parsing without the overhead of heavy browser automation.
- 🛡️ **Polite & Ethical Scraping**: Built-in randomized request throttling and dynamic user-agent pooling.
- 📋 **Deep Field Extraction**:
  - Job Title, Company Name, Geographic Location
  - Full Job Description (cleaned & formatted)
  - Seniority Level (Entry, Mid-Senior, Executive, Associate)
  - Employment Type (Full-time, Contract, Part-time)
  - Job Function & Industry Classification
  - Direct Application URLs & Canonical Job IDs
- 📊 **Multi-Format Export**:
  - **Formatted Excel (`.xlsx`)**: Custom auto-fitted columns, description wrapping, and formatted headers.
  - **Clean CSV (`.csv`)**: UTF-8 with BOM encoded for seamless import into Pandas, Excel, or SQL databases.

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/Nikhiljella/job_hunt.git
cd job_hunt

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Job Searches

**Search for Software Engineering roles in Edinburgh:**
```bash
python scrape_linkedin_jobs.py --title "Software Engineer" --location "Edinburgh, United Kingdom" --max-jobs 50
```

**Search for Data Scientists in Glasgow:**
```bash
python scrape_linkedin_jobs.py --title "Data Scientist" --location "Glasgow, United Kingdom" --max-jobs 30
```

**Search for Tech roles in London:**
```bash
python scrape_linkedin_jobs.py --title "Software Engineer" --location "London, United Kingdom" --max-jobs 100
```

**Search for Developers in Hyderabad:**
```bash
python scrape_linkedin_jobs.py --title "Software Engineer" --location "Hyderabad, India" --max-jobs 100
```

---

## 🛠️ CLI Options

| Argument | Short Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| `--title` | `-t` | Keywords or Job Title (e.g., `"Data Engineer"`) | `""` (All roles) |
| `--location` | `-l` | Target City, State, or Country | `"Glasgow, United Kingdom"` |
| `--max-jobs` | `-m` | Target number of unique listings to collect | `150` |

---

## 🗺️ Roadmap & Upcoming Features

- [ ] **AI-Powered Resume Matching**: Semantic similarity scoring between applicant resumes and extracted job descriptions using embeddings/LLMs.
- [ ] **Multi-Platform Support**: Expanding connectors to include Indeed, Wellfound (AngelList), and RemoteOK.
- [ ] **Automated Alerts**: Email and Telegram notifications for high-priority matching job leads.
- [ ] **Interactive TUI Dashboard**: Terminal-based user interface for reviewing and bookmarking listings.

---

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are very welcome! Please feel free to open an issue or submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
