# 🚀 JobHunter AI — Autonomous Job Discovery & Application Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-automated-green.svg)](https://playwright.dev/)
[![Flask Dashboard](https://img.shields.io/badge/dashboard-flask-black.svg)](http://127.0.0.1:5000)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An autonomous Python engine designed to streamline and accelerate software engineering job searches:
1. **Real-time Discovery**: Crawls and aggregates remote & regional tech job postings across public APIs (Remotive, Arbeitnow, Jobicy, GitHub Issues).
2. **Deterministic Matching**: Scores vacancies against your exact technical profile, stack, and seniority level using a customizable weighted algorithm.
3. **Tailored Application Kits**: Dynamically crafts personalized, ATS-friendly Cover Letters and pre-fills answers for common form platforms (Ashby, Greenhouse, Lever, Gupy).
4. **Supervised Browser Auto-Filler**: Uses Playwright to navigate directly to application forms and auto-populate candidate details, attachments, and links.
5. **Interactive Web Dashboard**: Modern Flask web UI for filtering, viewing matches, and launching 1-click actions.

---

## 📂 Project Architecture

```text
JobHunterAi/
├── app.py                      # Modern Web Dashboard (Flask + Tailwind)
├── fetcher.py                  # Public job feed crawlers & caching
├── matcher.py                  # Scoring & relevance algorithm (0–100%)
├── generator.py                # Cover letter & ATS answer generator
├── autofill.py                 # Playwright browser form auto-filler
├── email_sender.py             # 1-click Webmail & application draft generator
├── main.py                     # CLI entrypoint
├── profile.example.json        # Template candidate profile (copy to profile.json)
├── requirements.txt            # Python dependencies
├── run_dashboard.bat           # 1-click Windows launcher
└── examples/                   # Sample ATS-optimized Resumes (PT & EN)
    ├── curriculo_exemplo.html  # 1-page A4 ATS template (Portuguese)
    ├── curriculo_exemplo.pdf   # Rendered PDF sample
    ├── resume_example.html     # 1-page US Letter ATS template (English)
    └── resume_example.pdf      # Rendered PDF sample
```

---

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/VitorManuel01/JobHunterAi.git
cd JobHunterAi
```

### 2. Install Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Your Candidate Profile
Copy the example profile and personalize it with your skills, links, and portfolio:
```bash
cp profile.example.json profile.json
```

---

## 🖥️ Running the Web Dashboard

Launch the visual dashboard with a single command:
```bash
python app.py
```
*(Or double-click `run_dashboard.bat` on Windows).*

The browser automatically opens `http://127.0.0.1:5000`:
- **Match Breakdown**: View compatibility scores, badges, and salary indicators.
- **Tech Filtering**: Filter by Java, Python, Flutter, SQL, Remote, and more.
- **Live Cover Letters**: Preview custom cover letters generated for each opportunity.
- **1-Click Auto-Fill**: Launch supervised Playwright sessions directly from the UI.

---

## ⌨️ Command Line Interface (CLI)

You can also operate JobHunter AI entirely via terminal:

### Search & Rank Openings
```bash
# Fetch and rank the top 10 matching jobs
python main.py search --limit 10

# Force cache refresh from live APIs
python main.py search --refresh --limit 15
```

### Inspect a Specific Job
```bash
python main.py view <job_id>
# Example:
python main.py view remotive_2091158
```

### Generate Application Kit (Cover Letter + ATS Answers)
```bash
python main.py apply <job_id>
```
Generates ready-to-use artifacts under `applications/`:
- Tailored cover letter highlighting relevant portfolio repositories.
- Pre-filled answers for salary expectation, start date, and technical questions.

### Supervised Form Auto-Filler (Playwright)
```bash
python main.py autofill <job_id_or_url>
# Example:
python main.py autofill "https://jobs.lever.co/company/job-id"
```
Opens a visible browser session, locates form fields, fills candidate information, attaches your resume PDF, and leaves the tab open for human review before final submission.

---

## 📄 ATS Resume Templates Included

This repository bundles two reference 1-page ATS-optimized resumes in `examples/`:
- **`examples/curriculo_exemplo.pdf`**: Tailored for Brazilian tech roles (A4 standard, clean typography, zero multi-column parsing traps).
- **`examples/resume_example.pdf`**: Tailored for international remote roles (US Letter standard, impact-driven bullet points).

---

## 🔒 Privacy & Security

Your real data stays local:
- `profile.json`, `.env`, and private PDF resumes are strictly excluded via `.gitignore`.
- Only sanitized example templates (`profile.example.json` and `examples/`) are tracked in version control.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
