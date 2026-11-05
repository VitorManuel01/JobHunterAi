"""
Job Fetcher Module (Global Multi-Region Remote Tech Scraper)
Fetches remote tech jobs worldwide across:
- Europe & EMEA (Arbeitnow, Jobicy Europe/UK, Canonical, Elastic)
- Asia & APAC (Jobicy APAC, Hacker News Asian Startups)
- Latin America & Brazil (Jobicy LatAm, RemoteOK)
- Global & Worldwide (We Work Remotely, Himalayas, Hacker News, Greenhouse)
"""

import html
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "jobs.json")

EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
EMAIL_BLACKLIST = ['example.com', 'domain.com', 'yourname@', 'email@', 'support@', 'privacy@', 'help@', 'press@', 'legal@', 'abuse@', 'security@', 'accommodation', 'disability', 'eeo@', 'compliance@']

def extract_contact_email(text: str) -> str:
    """Extracts genuine application email address from job text, filtering out boilerplate emails."""
    if not text:
        return ""
    matches = EMAIL_REGEX.findall(text)
    for m in matches:
        low = m.lower()
        if not any(b in low for b in EMAIL_BLACKLIST):
            return m
    return ""

def clean_html(raw_html: str) -> str:
    """Removes HTML tags, decodes entities, and normalizes whitespace."""
    if not raw_html:
        return ""
    clean_re = re.compile(r"<.*?>")
    text = re.sub(clean_re, " ", raw_html)
    text = html.unescape(text)
    return " ".join(text.split())

def enrich_region_tags(location: str, tags: List[str]) -> List[str]:
    """Appends regional tags based on location text for instant multi-region filtering."""
    loc_low = location.lower()
    t_set = set(t.lower() for t in tags)
    
    if any(k in loc_low for k in ["europe", "eu", "uk", "united kingdom", "germany", "france", "netherlands", "spain", "berlin", "london", "switzerland", "ireland", "emea", "poland", "czech", "sweden", "norway"]):
        t_set.add("europe")
        t_set.add("europa")
    
    if any(k in loc_low for k in ["asia", "apac", "japan", "singapore", "india", "philippines", "vietnam", "australia", "tokyo", "korea", "taiwan", "indonesia"]):
        t_set.add("asia")
        t_set.add("apac")

    if any(k in loc_low for k in ["latam", "latin america", "brazil", "brasil", "são paulo", "sao paulo", "rio de janeiro", "curitiba", "belo horizonte", "salvador", "florianópolis", "florianopolis", "porto alegre", "recife", "campinas", "argentina", "colombia", "chile", "mexico", "americas"]):
        t_set.add("latam")
        t_set.add("americas")
        if any(k in loc_low for k in ["brazil", "brasil", "são paulo", "sao paulo", "rio de janeiro", "curitiba", "belo horizonte", "salvador", "florianópolis", "florianopolis", "porto alegre", "recife", "campinas"]):
            t_set.add("brasil")
            t_set.add("brazil")

    if any(k in loc_low for k in ["anywhere", "worldwide", "global", "remote"]):
        t_set.add("worldwide")
        t_set.add("global")

    return list(t_set)

def fetch_json(url: str, timeout: int = 12) -> Any:
    """Helper to fetch and parse JSON with a standard browser User-Agent."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def fetch_remotive() -> List[Dict[str, Any]]:
    """Fetches remote software development jobs from Remotive API."""
    jobs = []
    try:
        url = "https://remotive.com/api/remote-jobs?category=software-dev"
        data = fetch_json(url)
        for item in data.get("jobs", []):
            desc = clean_html(item.get("description", ""))
            loc = item.get("candidate_required_location", "Anywhere")
            tags = enrich_region_tags(loc, [t.lower() for t in item.get("tags", [])] + ["remotive", "software"])
            apply_email = extract_contact_email(desc)
            jobs.append({
                "id": f"remotive_{item.get('id')}",
                "source": "Remotive",
                "title": item.get("title", ""),
                "company": item.get("company_name", ""),
                "url": item.get("url", ""),
                "location": loc,
                "tags": tags,
                "description": desc,
                "salary": item.get("salary", "USD Competitive"),
                "apply_email": apply_email,
                "published_at": item.get("publication_date", "")
            })
    except Exception as e:
        print(f"[!] Warning: Remotive API error: {e}")
    return jobs

def fetch_arbeitnow() -> List[Dict[str, Any]]:
    """Fetches European remote tech jobs from Arbeitnow (multi-page)."""
    jobs = []
    for page in range(1, 4):
        try:
            url = f"https://www.arbeitnow.com/api/job-board-api?page={page}"
            data = fetch_json(url, timeout=10)
            for item in data.get("data", []):
                if not item.get("remote", False):
                    continue
                desc = clean_html(item.get("description", ""))
                apply_email = extract_contact_email(desc)
                loc = item.get("location", "Europe (Remote)")
                tags = enrich_region_tags(loc, [t.lower() for t in item.get("tags", [])] + ["arbeitnow", "europe"])
                jobs.append({
                    "id": f"arbeitnow_{item.get('slug', '')[:30]}",
                    "source": "Arbeitnow (Europe)",
                    "title": item.get("title", ""),
                    "company": item.get("company_name", ""),
                    "url": item.get("url", ""),
                    "location": loc,
                    "tags": tags,
                    "description": desc,
                    "salary": "EUR Competitive",
                    "apply_email": apply_email,
                    "published_at": item.get("created_at", "")
                })
        except Exception as e:
            print(f"[!] Warning: Arbeitnow page {page} error: {e}")
    return jobs

def fetch_jobicy() -> List[Dict[str, Any]]:
    """Fetches remote tech jobs across Europe, APAC (Asia), LatAm, UK, and Worldwide from Jobicy."""
    jobs = []
    geos = [
        ("europe", "Europe"),
        ("apac", "Asia-Pacific / APAC"),
        ("latam", "Latin America"),
        ("uk", "United Kingdom"),
        ("anywhere", "Worldwide")
    ]
    for geo_code, geo_label in geos:
        try:
            url = f"https://jobicy.com/api/v2/remote-jobs?count=50&geo={geo_code}"
            data = fetch_json(url, timeout=10)
            for item in data.get("jobs", []):
                industry_raw = item.get("jobIndustry", "")
                if isinstance(industry_raw, list):
                    base_tags = [str(t).strip().lower() for t in industry_raw if str(t).strip()]
                else:
                    base_tags = [t.strip().lower() for t in str(industry_raw).split(",") if t.strip()]

                loc = item.get("jobGeo", geo_label)
                tags = enrich_region_tags(loc, base_tags + ["jobicy", geo_code])
                desc = clean_html(item.get("jobDescription", ""))
                apply_email = extract_contact_email(desc)

                jobs.append({
                    "id": f"jobicy_{item.get('id')}",
                    "source": f"Jobicy ({geo_label})",
                    "title": item.get("jobTitle", ""),
                    "company": item.get("companyName", ""),
                    "url": item.get("url", ""),
                    "location": loc,
                    "tags": tags,
                    "description": desc,
                    "salary": f"{item.get('annualSalaryMin', '')} - {item.get('annualSalaryMax', '')} {item.get('salaryCurrency', '')}".strip(" -") or "Competitive",
                    "apply_email": apply_email,
                    "published_at": item.get("pubDate", "")
                })
        except Exception as e:
            print(f"[!] Warning: Jobicy {geo_code} error: {e}")
    return jobs

def fetch_wwr() -> List[Dict[str, Any]]:
    """Fetches global remote programming jobs from We Work Remotely (WWR) RSS feeds."""
    feeds = [
        ("https://weworkremotely.com/categories/remote-programming-jobs.rss", "Programming"),
        ("https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss", "Full-Stack"),
        ("https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss", "Backend"),
        ("https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss", "DevOps/Support")
    ]
    jobs = []
    for feed_url, cat_name in feeds:
        try:
            req = urllib.request.Request(feed_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item"):
                    raw_title = item.find("title").text if item.find("title") is not None else ""
                    raw_link = item.find("link").text if item.find("link") is not None else ""
                    raw_desc = item.find("description").text if item.find("description") is not None else ""
                    region = item.find("region").text if item.find("region") is not None else "Anywhere in the World"
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

                    if ":" in raw_title:
                        parts = raw_title.split(":", 1)
                        company = parts[0].strip()
                        title = parts[1].strip()
                    else:
                        company = "Remote Tech"
                        title = raw_title

                    clean_desc = clean_html(raw_desc)
                    apply_email = extract_contact_email(clean_desc)
                    tags = enrich_region_tags(region, ["remote", "wwr", cat_name.lower()])

                    jobs.append({
                        "id": f"wwr_{abs(hash(raw_link)) % 10000000}",
                        "source": "We Work Remotely",
                        "title": title,
                        "company": company,
                        "url": raw_link,
                        "location": region,
                        "tags": tags,
                        "description": clean_desc,
                        "salary": "USD Competitive",
                        "apply_email": apply_email,
                        "published_at": pub_date
                    })
        except Exception as e:
            print(f"[!] Warning: WWR feed {cat_name} error: {e}")
    return jobs

def fetch_himalayas() -> List[Dict[str, Any]]:
    """Fetches global remote positions from Himalayas API."""
    jobs = []
    try:
        url = "https://himalayas.app/jobs/api?limit=50"
        data = fetch_json(url, timeout=10)
        for item in data.get("jobs", []):
            title = item.get("title", "")
            company = item.get("companyName", "")
            desc = clean_html(item.get("description", item.get("excerpt", "")))
            locs = item.get("locationRestrictions", [])
            location = ", ".join(locs) if locs else "Worldwide Remote"
            target_url = item.get("applicationLink") or item.get("guid") or f"https://himalayas.app/companies/{item.get('companySlug')}/jobs"
            apply_email = extract_contact_email(desc)
            tags = enrich_region_tags(location, [str(c).lower() for c in item.get("categories", [])] + ["himalayas"])

            jobs.append({
                "id": f"himalayas_{item.get('guid', '')[-20:]}",
                "source": "Himalayas",
                "title": title,
                "company": company,
                "url": target_url,
                "location": location,
                "tags": tags,
                "description": desc,
                "salary": f"{item.get('minSalary', '')} - {item.get('maxSalary', '')} {item.get('currency', 'USD')}".strip(" -") or "USD Competitive",
                "apply_email": apply_email,
                "published_at": item.get("pubDate", "")
            })
    except Exception as e:
        print(f"[!] Warning: Himalayas API error: {e}")
    return jobs

def fetch_remoteok() -> List[Dict[str, Any]]:
    """Fetches remote jobs from RemoteOK API."""
    jobs = []
    try:
        url = "https://remoteok.com/api"
        data = fetch_json(url, timeout=10)
        for item in data:
            if not isinstance(item, dict) or not item.get("position"):
                continue
            desc = clean_html(item.get("description", ""))
            apply_url = item.get("apply_url", "")
            apply_email = ""
            if "@" in apply_url and "http" not in apply_url:
                apply_email = apply_url.replace("mailto:", "").strip()
            else:
                apply_email = extract_contact_email(desc)
            
            loc = item.get("location", "Remote")
            tags = enrich_region_tags(loc, [str(t).lower() for t in item.get("tags", [])] + ["remoteok"])

            jobs.append({
                "id": f"remoteok_{item.get('id')}",
                "source": "RemoteOK",
                "title": item.get("position", ""),
                "company": item.get("company", ""),
                "url": item.get("url", apply_url),
                "location": loc,
                "tags": tags,
                "description": desc,
                "salary": item.get("salary", "USD Competitive"),
                "apply_email": apply_email,
                "published_at": str(item.get("date", ""))
            })
    except Exception as e:
        print(f"[!] Warning: RemoteOK API error: {e}")
    return jobs

def fetch_hn_hiring() -> List[Dict[str, Any]]:
    """
    Fetches startup jobs from the latest 4 Hacker News 'Ask HN: Who is hiring?' threads,
    covering founders and CTOs hiring across Asia, Europe, Americas, and Worldwide with direct emails.
    """
    jobs = []
    try:
        url = "https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query=Who%20is%20hiring&hitsPerPage=6"
        data = fetch_json(url, timeout=10)
        stories = [s for s in data.get("hits", []) if "Who is hiring?" in s.get("title", "")]

        for s in stories[:4]:
            s_id = s["objectID"]
            c_url = f"https://hn.algolia.com/api/v1/search?tags=comment,story_{s_id}&hitsPerPage=500"
            c_data = fetch_json(c_url, timeout=14)

            for c in c_data.get("hits", []):
                raw_text = c.get("comment_text", "")
                if not raw_text or "remote" not in raw_text.lower():
                    continue

                clean = clean_html(raw_text)
                apply_email = extract_contact_email(clean)
                if not apply_email:
                    continue

                # Parse header line (Company | Role | Location)
                first_line = clean.split(". ")[0]
                parts = [p.strip() for p in first_line.split("|")]

                company = parts[0] if parts else "Tech Startup"
                title = "Software Engineer"
                for p in parts[1:]:
                    p_low = p.lower()
                    if any(r in p_low for r in ["engineer", "developer", "specialist", "ai", "full-stack", "backend", "frontend", "mobile"]):
                        title = p
                        break
                else:
                    if len(parts) > 1:
                        title = parts[1]

                location = parts[2] if len(parts) > 2 else "Remote"
                tags = enrich_region_tags(f"{location} {clean[:200]}", ["hacker news", "startup", "email application", "software"])

                jobs.append({
                    "id": f"hn_{c.get('objectID')}",
                    "source": "Hacker News (Who is Hiring)",
                    "title": title[:70],
                    "company": company[:50],
                    "url": f"https://news.ycombinator.com/item?id={c.get('objectID')}",
                    "location": location,
                    "tags": tags,
                    "description": clean,
                    "salary": "USD Competitive",
                    "apply_email": apply_email,
                    "published_at": c.get("created_at", "")
                })
    except Exception as e:
        print(f"[!] Warning: Hacker News hiring fetch error: {e}")
    return jobs

# Top global and Brazilian tech companies hiring on Greenhouse (100% Direct, Free ATS — No Subscriptions)
GREENHOUSE_BOARDS = [
    # Global Tech Unicorns & Remote Leaders
    ("canonical", "Canonical (Ubuntu)"),
    ("gitlab", "GitLab"),
    ("stripe", "Stripe"),
    ("cloudflare", "Cloudflare"),
    ("reddit", "Reddit"),
    ("figma", "Figma"),
    ("discord", "Discord"),
    ("datadog", "Datadog"),
    ("mozilla", "Mozilla"),
    ("cockroachlabs", "Cockroach Labs"),
    ("wikimedia", "Wikimedia Foundation"),
    ("elastic", "Elastic"),
    # Brazilian Tech Leaders & Unicorns (100% Free Greenhouse ATS)
    ("stone", "Stone Pagamentos"),
    ("inter", "Banco Inter"),
    ("quintoandar", "QuintoAndar"),
    ("gympass", "Wellhub (Gympass)"),
    ("ebanx", "EBANX"),
    ("vtex", "VTEX"),
    ("wildlifestudios", "Wildlife Studios")
]

def fetch_greenhouse() -> List[Dict[str, Any]]:
    """Fetches remote tech postings from major Greenhouse job boards worldwide & Brazil (100% Direct ATS)."""
    jobs = []
    for board_token, company_name in GREENHOUSE_BOARDS:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
            data = fetch_json(url, timeout=10)
            for item in data.get("jobs", []):
                loc_name = item.get("location", {}).get("name", "") if isinstance(item.get("location"), dict) else str(item.get("location", ""))
                loc_lower = loc_name.lower()
                # Filter for remote / global / regional / Brazilian roles
                if any(k in loc_lower for k in [
                    "remote", "home", "anywhere", "global", "americas", "emea", "apac",
                    "brazil", "brasil", "latin america", "europe", "uk", "asia",
                    "são paulo", "sao paulo", "rio de janeiro", "curitiba", "belo horizonte",
                    "salvador", "florianópolis", "florianopolis", "porto alegre", "recife", "campinas"
                ]):
                    tags = enrich_region_tags(loc_name, [board_token, "greenhouse", "software"])
                    salary = "R$ Competitivo (CLT/PJ)" if any(k in loc_lower for k in ["brazil", "brasil", "são paulo", "sao paulo", "rio de janeiro", "curitiba", "belo horizonte", "salvador", "florianópolis", "porto alegre"]) else "Competitive (USD/EUR)"
                    jobs.append({
                        "id": f"gh_{board_token}_{item.get('id')}",
                        "source": f"Greenhouse ({company_name})",
                        "title": item.get("title", ""),
                        "company": company_name,
                        "url": item.get("absolute_url", ""),
                        "location": loc_name or "Remote Worldwide",
                        "tags": tags,
                        "description": f"{item.get('title')} at {company_name}. Location: {loc_name}",
                        "salary": salary,
                        "published_at": item.get("updated_at", "")
                    })
        except Exception as e:
            print(f"[!] Warning: Greenhouse board {board_token} error: {e}")
    return jobs

def fetch_github_vagas_br() -> List[Dict[str, Any]]:
    """
    Fetches genuine open tech positions from Brazil's most popular developer job boards on GitHub:
    - backend-br/vagas
    - frontendbr/vagas
    These repositories aggregate direct developer jobs, junior/internship roles, and email applications.
    """
    jobs = []
    repos = [
        ("backend-br/vagas", "GitHub (backend-br)"),
        ("frontendbr/vagas", "GitHub (frontendbr)")
    ]

    for repo_name, source_label in repos:
        try:
            url = f"https://api.github.com/repos/{repo_name}/issues?state=open&per_page=50"
            data = fetch_json(url, timeout=12)
            for item in data:
                if "pull_request" in item:
                    continue

                raw_title = item.get("title", "").strip()
                body = item.get("body") or ""
                clean_desc = clean_html(body)
                labels = [l.get("name", "") for l in item.get("labels", [])]

                # Extract direct application email if specified in the issue
                apply_email = extract_contact_email(body)

                # Infer company name from title pattern e.g. "[Remoto] Dev na EmpresaX" or "EmpresaX contrata..."
                company = "Empresa de Tecnologia (BR)"
                company_match = re.search(r'\b(?:na|no|at|em|pela)\s+([A-Za-z0-9\.\-_\s]{2,25})\b', raw_title, re.IGNORECASE)
                if company_match:
                    company = company_match.group(1).strip()
                elif "@" in raw_title:
                    company = raw_title.split("@")[-1].strip()

                # Infer location
                location = "Brasil (Remoto)"
                if any(k in raw_title.lower() for k in ["híbrido", "hibrido"]):
                    location = "Brasil (Híbrido)"
                elif any(k in raw_title.lower() for k in ["são paulo", "sp", "rio de janeiro", "rj", "curitiba", "salvador", "belo horizonte"]):
                    location = "Brasil"

                tags = enrich_region_tags(f"{location} {raw_title}", [l.lower() for l in labels] + ["brasil", "vagas-br", "nacional"])
                if apply_email:
                    tags.append("email application")

                jobs.append({
                    "id": f"gh_issue_{repo_name.replace('/', '_')}_{item.get('number')}",
                    "source": source_label,
                    "title": raw_title,
                    "company": company,
                    "url": item.get("html_url", ""),
                    "location": location,
                    "tags": tags,
                    "description": clean_desc if clean_desc else raw_title,
                    "salary": "R$ Competitivo (CLT / PJ)",
                    "apply_email": apply_email,
                    "published_at": item.get("created_at", "")
                })
        except Exception as e:
            print(f"[!] Warning: GitHub vagas BR error for {repo_name}: {e}")

    return jobs

def fetch_all_jobs(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Fetches jobs strictly from 100% FREE & DIRECT sources (Direct ATS, GitHub Vagas BR, and Founder Emails).
    Zero paywalls, zero registration gates, zero subscriptions.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if cached:
                    return cached
        except Exception:
            pass

    print("[*] Fetching fresh jobs strictly from 100% FREE & DIRECT platforms (Greenhouse Global & BR, GitHub Vagas BR, Hacker News, Arbeitnow ATS)...")
    all_jobs = []
    all_jobs.extend(fetch_greenhouse())        # Canonical, GitLab, Stripe, Stone, Banco Inter, QuintoAndar, Wellhub, etc.
    all_jobs.extend(fetch_github_vagas_br())   # backend-br/vagas, frontendbr/vagas (Junior, CLT/PJ, Direct emails)
    all_jobs.extend(fetch_hn_hiring())         # Hacker News direct founder/CTO emails
    all_jobs.extend(fetch_arbeitnow())         # Arbeitnow (Direct Recruitee/Lever ATS redirects)

    # Deduplicate by URL or title + company
    seen = set()
    deduped = []
    for j in all_jobs:
        key = (j["title"].lower().strip(), j["company"].lower().strip())
        if key not in seen and j["title"]:
            seen.add(key)
            deduped.append(j)

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully collected and cached {len(deduped)} free & direct remote jobs.")
    return deduped

if __name__ == "__main__":
    jobs = fetch_all_jobs(force_refresh=True)
    print(f"Total jobs: {len(jobs)}")
