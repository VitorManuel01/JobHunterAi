"""
Job Matcher Module (Strict Junior & Vibe Coding / AI-Assisted Filter)

Enforces STRICT disqualifications:
1. All Senior, Lead, Staff, Principal, and 3+ years experience roles.
2. All Pure Machine Learning / Data Science / Quant Research roles (e.g. ML Engineer, Computer Vision, Data Scientist).
3. All Country-Restricted roles: "US only", "[Country] only", "[Region] only",
   "Remote (US)", "US-Remote", "W2 only", and domestic work authorization requirements.
4. All Non-technical roles (Sales, Recruiter, Talent Acquisition, Broker Dealer, HR, Finance).

Keeps and prioritizes:
1. AI-Assisted Software Engineering & Vibe Coding (Cursor, Copilot, Claude Code, Agentic Systems, AI Coding Tasks, LLM Integrations).
2. Junior / Entry-Level / Graduate / Associate Software Developers (C#, Java, Flutter, Python, Full-Stack, Backend, IT Support).
3. 100% Worldwide Remote, Anywhere in the World, Global, or LatAm / Brazil inclusive roles.
"""

import json
import os
import re
from typing import List, Dict, Any

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "profile.json")

def load_profile() -> Dict[str, Any]:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# 1. Senior, Leadership, and Experience Disqualifiers (3+ years strictly excluded)
SENIOR_EXPERIENCE_DISQUALIFIERS = [
    # Senior / Leadership / Executive titles
    (r"\b(senior|sr\.?|lead|tech lead|principal|staff|architect|director|head of|vp of|manager)\b", "Senior/Lead/Architect role (Not Junior)"),
    
    # Experience thresholds >= 3 years
    (r"\b(3\+|4\+|5\+|6\+|7\+|8\+|10\+|12\+)\s*(years?|yrs)\b", "Requires 3+ years of experience (Not Junior)"),
    (r"\b(at\s+least|minimum|min\.?)\s*(3|4|5|6|7|8|10)\s*(years?|yrs)\b", "Requires minimum 3+ years of experience"),
    (r"\b(3\s*-\s*5|3\s*to\s*5|4\s*-\s*6|4\s*to\s*6)\s*(years?|yrs)\b", "Requires 3-5+ years of experience (Not Junior)"),
    (r"\b(3|4|5|6|7|8|10)\s+years?\s+of\s+(commercial|professional|relevant|software|proven|industry|working)\s+experience\b", "Requires 3+ years of professional experience")
]

# 2. Pure Machine Learning & Data Science Research Disqualifiers
# The candidate is an AI-ASSISTED Software Engineer / Vibe Coder, NOT an ML Scientist / Researcher
ML_RESEARCH_DISQUALIFIERS = [
    (r"\b(machine\s+learning\s+engineer|ml\s+engineer|mle\b|data\s+scientist|quantitative\s+researcher|quant\s+researcher|computer\s+vision|deep\s+learning\s+engineer|ai\s+researcher|research\s+scientist|nlp\s+engineer|nlp\s+researcher)\b", "Pure ML/Data Science research role (Not Software Engineering / Vibe Coding)"),
    (r"\bsecurity,\s*machine\s+learning\b", "Machine Learning research role"),
    (r"\bmachine\s+learning\b", "Pure Machine Learning model training/research role")
]

# 3. Non-Technical Disqualifiers (Sales, Marketing, HR, Recruiter, Broker, Finance, PM, Designer, Ops)
NON_TECH_DISQUALIFIERS = [
    (r"\b(sales|sdr\b|bdr\b|account\s+executive|talent\s+acquisition|recruiter|recruiting|people\s+operations|hr\s+generalist|human\s+resources|recursos\s+humanos|departamento\s+pessoal|broker\s+dealer|brokerage|legal\s+counsel|accountant|bookkeeper|financial\s+analyst|payroll|ads\s+specialist|campaign\s+manager|marketing|seo\b|copywriter|content\s+writer|content\s*&\s*crm|crm\s+analyst|crm\b|project\s+manager|product\s+manager|ux/ui\s+designer|ui/ux\s+designer|graphic\s+designer|product\s+designer|social\s+media|faturamento|cobrança|cobranca|crédito|credit\s+business|credit\s+analyst|políticas\s+de\s+crédito|control\s+desk|customer\s+service|atendimento|telemarketing|vendas|comercial|consultor\s+comercial|agente\s+comercial|agente\s+stone|contábil|contabil|fiscal|financeiro|facilities|logística|logistica|operações|operacoes)\b", "Non-technical role (Sales/Marketing/HR/Design/PM/Ops/Finance)")
]

# 4. Paywalled & Subscription-Gated Job Boards (Hard Disqualification)
# Sites that require an account registration, credit card, or paid subscription to view/apply
SUBSCRIPTION_PAYWALLED_DOMAINS = [
    r"weworkremotely\.com",
    r"jobicy\.com",
    r"remoteok\.com",
    r"remotive\.com",
    r"himalayas\.app",
    r"flexjobs\.com",
    r"wellfound\.com"
]

# 5. Country & Region names for "Country only" exclusion
RESTRICTED_COUNTRIES = [
    r'us', r'usa', r'u\.s\.a?', r'united states', r'america',
    r'uk', r'u\.k\.', r'united kingdom', r'great britain', r'britain', r'england', r'scotland',
    r'canada', r'germany', r'deutschland', r'france', r'spain', r'italy', r'netherlands', r'switzerland', r'poland',
    r'sweden', r'norway', r'denmark', r'finland', r'ireland', r'austria', r'belgium', r'portugal', r'czech',
    r'india', r'pakistan', r'australia', r'nz', r'new zealand', r'japan', r'singapore', r'philippines', r'china',
    r'kenya', r'nigeria', r'south africa', r'ghana', r'egypt',
    r'north america', r'emea', r'apac', r'eu', r'europe'
]
C_REGEX = '|'.join(RESTRICTED_COUNTRIES)

COUNTRY_ONLY_DISQUALIFIERS = [
    # Explicit [Country] only, [Country]-only, [Country] based only, [Country] residents only
    (rf"\b({C_REGEX})\s*(only|-only|\s*based only|\s*citizens? only|\s*residents? only)\b", "Restricted to specific Country/Region only (e.g. US only)"),
    
    # Only in / only for / only open to [Country]
    (rf"\bonly\s+(in|for|from|to|candidates in|open to)\s+(the\s+)?({C_REGEX})\b", "Only open to candidates in specified Country/Region"),
    
    # Must reside in / must be based in / must be located in [Country]
    (rf"\b(must\s+reside\s+in|must\s+be\s+based\s+in|must\s+be\s+located\s+in|based\s+in)\s+(the\s+)?({C_REGEX})\b", "Must reside/be based in specific Country"),
    
    # Remote - [Country] Only / Remote ([Country] only)
    (rf"remote\s*[-–—:\(]\s*({C_REGEX})\s*only\b", "Remote position restricted to single country only"),
    
    # Domestic single country remote without global option (e.g. 'Remote (US)', 'US-Remote', 'Remote - US', 'Remote, United States')
    (r"\b(remote\s*[\(,-]\s*(us|usa|united states|uk|canada)\b|\b(us|usa|uk|canada)[\s-]*remote\b)", "Single-country domestic remote (Not international)"),
    
    # Work authorization / citizenship / clearance requirements
    (r"\b(work\s+authorization\s+required|right\s+to\s+work\s+in|must\s+be\s+authorized\s+to\s+work\s+in\s+the\s+u\.?s\.?|us\s+citizenship\s+required|us\s+citizens?\s+only|security\s+clearance|top\s+secret|w2\s+only|w-2\s+only)\b", "Requires domestic work authorization or citizenship")
]

# Exceptions: titles that contain 'senior' but also explicitly include 'junior' (e.g. "Junior/Mid/Senior" or "All Levels")
EXCEPTION_PATTERNS = [
    r"\bjunior\b",
    r"\bjr\.?\b",
    r"\bentry\b",
    r"\bintern\b",
    r"\ball levels\b"
]

# Strictly AI-Assisted Software Engineering & Vibe Coding keywords (Highest Priority)
# NOTE: Pure "machine learning" is deliberately EXCLUDED here!
AI_VIBE_KEYWORDS = {
    "vibe coding": 55,
    "vibe code": 55,
    "ai coding": 50,
    "ai assisted": 50,
    "ai-assisted": 50,
    "ai coding tasks": 45,
    "ai tasks": 40,
    "ai task": 40,
    "ai application": 45,
    "ai engineer (agentic": 45,
    "agentic": 40,
    "cursor": 40,
    "copilot": 35,
    "claude": 35,
    "llm evaluation": 35,
    "code evaluation": 35,
    "prompt engineer": 35,
    "llm": 25,
    "generative ai": 25,
    "synthetic data": 20
}

# Junior & Entry-Level keywords (Including Portuguese / Brazilian tech terms)
JUNIOR_KEYWORDS = {
    "junior": 50,
    "jr": 50,
    "júnior": 50,
    "estágio": 45,
    "estagio": 45,
    "estagiário": 45,
    "estagiaria": 45,
    "trainee": 40,
    "entry level": 45,
    "entry-level": 45,
    "associate software": 40,
    "associate engineer": 40,
    "associate developer": 40,
    "associate": 30,
    "intern": 30,
    "internship": 30,
    "graduate developer": 35,
    "graduate engineer": 35,
    "early career": 30,
    "início de carreira": 35
}

# Core Stack keywords (Prioritizing candidate's verified skills: Java, Flutter/Dart, Python, SQL)
STACK_KEYWORDS = {
    "flutter": 35,
    "dart": 30,
    "java": 35,
    "spring": 30,
    "python": 30,
    "react": 15,
    "javascript": 12,
    "typescript": 15,
    "sql": 20,
    "mysql": 20,
    "postgresql": 20,
    "suporte": 20,
    "analista de sistemas": 20,
    "support engineer": 20,
    "technical support": 20
}

def analyze_job(job: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a single job and enforces:
    1. STRICT Junior + Vibe/AI filtering (Disqualifies Senior/Lead AND any 3+ years experience).
    2. STRICT Machine Learning Research exclusion (Disqualifies pure ML models, CV, Data Science).
    3. STRICT Non-Technical exclusion (Disqualifies Sales, SDR, Recruiter, Finance).
    4. STRICT Country-Only elimination (No 'US only', '[Country] only', or domestic work auth).
    """
    title = job.get('title', '').strip()
    title_lower = title.lower()
    description = job.get('description', '')
    desc_lower = description.lower()
    location = job.get('location', '')
    loc_lower = location.lower()
    tags = [t.lower() for t in job.get('tags', [])]
    full_text = f"{title_lower} {loc_lower} {' '.join(tags)} {desc_lower}"

    # Determine if job is based in Brazil / Brazilian tech market
    is_brazil = (
        any(k in loc_lower for k in [
            'brasil', 'brazil', 'são paulo', 'sao paulo', 'rio de janeiro', 'curitiba',
            'belo horizonte', 'salvador', 'florianópolis', 'florianopolis', 'porto alegre',
            'recife', 'campinas', 'remoto brasil'
        ])
        or any(t in ['brasil', 'brazil', 'portuguese', 'nacional', 'vagas-br', 'remoto brasil'] for t in tags)
        or 'github (backend-br' in job.get('source', '').lower()
        or 'github (frontendbr' in job.get('source', '').lower()
        or any(w in desc_lower for w in ['clt', 'pj', 'remoto brasil', 'benefícios', 'horário flexível', 'contratação clt', 'contratação pj', 'vale refeição'])
    )

    if is_brazil and "brasil" not in tags:
        tags.append("brasil")

    # Check for senior exceptions (e.g. title is "Junior/Mid/Senior" -> Allowed!)
    has_junior_exception = any(re.search(pat, title_lower) for pat in EXCEPTION_PATTERNS)

    # Check if job explicitly allows Worldwide, Anywhere, Global, Brazil, or LatAm
    has_global_pass = any(k in loc_lower for k in ['worldwide', 'anywhere', 'global', 'brazil', 'brasil', 'latam', 'latin america']) or is_brazil

    disqualified_reasons = []

    # 1. HARD NON-TECHNICAL DISQUALIFICATION (Sales, HR, Finance)
    for pattern, reason in NON_TECH_DISQUALIFIERS:
        if re.search(pattern, title_lower):
            disqualified_reasons.append(reason)
            break

    # 2. HARD PURE MACHINE LEARNING & DATA SCIENCE DISQUALIFICATION
    # If the title indicates ML research / Data Science / Computer Vision, reject immediately
    for pattern, reason in ML_RESEARCH_DISQUALIFIERS:
        if re.search(pattern, title_lower):
            # Only allow if it's explicitly an AI-assisted software engineer or vibe coding role
            if not any(k in title_lower for k in ['vibe', 'ai assisted', 'ai-assisted', 'ai coding', 'software engineer', 'developer']):
                disqualified_reasons.append(reason)
                break
            elif "machine learning" in title_lower and not any(k in title_lower for k in ['ai assisted', 'vibe', 'coding tasks']):
                disqualified_reasons.append(reason)
                break

    # 3. HARD SENIOR & EXPERIENCE DISQUALIFICATION (No 3+ years)
    for pattern, reason in SENIOR_EXPERIENCE_DISQUALIFIERS:
        if "Senior/Lead" in reason:
            if re.search(pattern, title_lower) and not has_junior_exception:
                disqualified_reasons.append(reason)
        else:
            # Experience threshold in description or title
            if re.search(pattern, desc_lower) or re.search(pattern, title_lower):
                disqualified_reasons.append(reason)

    # 4. HARD COUNTRY-ONLY DISQUALIFICATION
    # Check if location string explicitly specifies 'only' (e.g. "USA Only", "North America Only")
    if 'only' in loc_lower and not any(k in loc_lower for k in ['worldwide', 'global', 'anywhere', 'brazil', 'latam']):
        disqualified_reasons.append(f"Geographically restricted location: '{location}'")

    for pattern, reason in COUNTRY_ONLY_DISQUALIFIERS:
        if "only" in pattern or "authorization" in pattern:
            if re.search(pattern, full_text):
                disqualified_reasons.append(reason)
                break
        elif not has_global_pass:
            if re.search(pattern, full_text):
                disqualified_reasons.append(reason)
                break

    # 5. HARD SUBSCRIPTION & PAYWALL DISQUALIFICATION (No paywalls or registration gates)
    url_lower = job.get('url', '').lower()
    source_lower = job.get('source', '').lower()
    if any(re.search(dom, url_lower) for dom in SUBSCRIPTION_PAYWALLED_DOMAINS) or any(k in source_lower for k in ['weworkremotely', 'jobicy', 'remoteok', 'remotive', 'himalayas', 'flexjobs']):
        disqualified_reasons.append("Site requires account registration or paid subscription (e.g. WWR, Jobicy, RemoteOK, Remotive)")

    # 6. HARD C# / .NET DISQUALIFICATION (Candidate does not work with C# / .NET)
    if re.search(r'\b(c#|\.net|asp\.net|csharp|dotnet)\b', title_lower):
        disqualified_reasons.append("Job primarily requires C# / .NET (candidate requested exclusion)")

    if disqualified_reasons:
        return {
            "job_id": job.get("id"),
            "title": title,
            "company": job.get("company"),
            "url": job.get("url"),
            "source": job.get("source"),
            "location": job.get("location"),
            "tags": job.get("tags", []),
            "description": job.get("description", ""),
            "salary": job.get("salary", "Competitive"),
            "score": 0,
            "is_disqualified": True,
            "disqualified_reasons": disqualified_reasons,
            "category": "DISQUALIFIED",
            "is_brazilian": is_brazil,
            "matched_keywords": [],
            "recommended_project": profile["portfolio_projects"][0]
        }

    # 5. SCORE CALCULATION
    score = 0
    matched_keywords = []
    is_vibe_ai = False
    is_explicit_junior = False

    # AI & Vibe Coding Boost (Strictly AI-Assisted Software Dev)
    for kw, weight in AI_VIBE_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", title_lower):
            score += weight * 1.6
            matched_keywords.append(f"{kw} (in title)")
            is_vibe_ai = True
        elif re.search(r"\b" + re.escape(kw) + r"\b", full_text):
            score += weight * 0.7
            matched_keywords.append(kw)
            is_vibe_ai = True

    # Junior & Entry Level Boost
    for kw, weight in JUNIOR_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", title_lower):
            score += weight * 1.5
            matched_keywords.append(f"{kw} (in title)")
            is_explicit_junior = True
        elif re.search(r"\b" + re.escape(kw) + r"\b", full_text):
            score += weight * 0.5
            matched_keywords.append(kw)

    # Core Stack Matching
    for kw, weight in STACK_KEYWORDS.items():
        if re.search(r"\b" + re.escape(kw) + r"\b", title_lower):
            score += weight * 1.2
            matched_keywords.append(f"{kw} (in title)")
        elif re.search(r"\b" + re.escape(kw) + r"\b", full_text):
            score += weight * 0.4
            matched_keywords.append(kw)

    # Email Application Bonus (Direct founder/team access is high value)
    if job.get("apply_email"):
        score += 15
        matched_keywords.append("direct email application")

    # If it has neither Junior nor AI/Vibe keywords and low relevance
    if score == 0:
        return {
            "job_id": job.get("id"),
            "title": title,
            "company": job.get("company"),
            "url": job.get("url"),
            "source": job.get("source"),
            "location": job.get("location"),
            "tags": job.get("tags", []),
            "description": job.get("description", ""),
            "salary": job.get("salary", "Competitive"),
            "score": 0,
            "is_disqualified": False,
            "disqualified_reasons": ["Low relevance to Junior/AI profile"],
            "category": "LOW_MATCH",
            "is_brazilian": is_brazil,
            "matched_keywords": [],
            "recommended_project": profile["portfolio_projects"][0]
        }

    # Determine job category
    category = "SOFTWARE ENG"
    def has_kw(k):
        return any(k == m or m.startswith(f"{k} ") or f" {k} " in f" {m} " for m in matched_keywords)

    if is_vibe_ai:
        category = "AI ASSISTED DEV"
    elif has_kw("flutter") or has_kw("dart"):
        category = "FLUTTER / MOBILE"
    elif has_kw("java") or has_kw("spring"):
        category = "JAVA BACKEND"
    elif has_kw("python"):
        category = "PYTHON DEV"
    elif is_explicit_junior:
        category = "JUNIOR GENERAL"

    # Select recommended portfolio project
    if category == "AI ASSISTED DEV":
        matched_proj = next((p for p in profile["portfolio_projects"] if "FalloutRemake" in p["name"]), profile["portfolio_projects"][0])
    elif category == "FLUTTER / MOBILE":
        matched_proj = next((p for p in profile["portfolio_projects"] if p["name"] == "MemoryCare"), profile["portfolio_projects"][0])
    elif category == "JAVA BACKEND":
        matched_proj = next((p for p in profile["portfolio_projects"] if p["name"] == "Dubai Magazine Salvador"), profile["portfolio_projects"][0])
    elif category == "PYTHON DEV":
        matched_proj = next((p for p in profile["portfolio_projects"] if p["name"] == "NovaProfiles"), profile["portfolio_projects"][0])
    else:
        matched_proj = profile["portfolio_projects"][0] # Dubai Magazine Salvador as default showcase!

    final_score = min(100, int(score))
    apply_email = job.get("apply_email", "")

    return {
        "job_id": job.get("id"),
        "title": title,
        "company": job.get("company"),
        "url": job.get("url"),
        "source": job.get("source"),
        "location": job.get("location"),
        "tags": job.get("tags", []),
        "description": job.get("description", ""),
        "salary": job.get("salary", "Competitive"),
        "score": final_score,
        "apply_email": apply_email,
        "accepts_email": bool(apply_email),
        "is_disqualified": False,
        "disqualified_reasons": [],
        "category": category,
        "is_brazilian": is_brazil,
        "is_vibe_ai": is_vibe_ai,
        "is_explicit_junior": is_explicit_junior,
        "matched_keywords": list(set(matched_keywords)),
        "recommended_project": matched_proj
    }

def rank_jobs(jobs: List[Dict[str, Any]], min_score: int = 15) -> List[Dict[str, Any]]:
    """
    Ranks jobs by compatibility score.
    Strictly excludes:
    - Senior / Lead / Staff roles.
    - Any role requiring 3+ years of experience.
    - Pure Machine Learning / Data Science / Quant Research.
    - Non-technical roles (Sales/HR/Recruiter).
    - Country-restricted roles (US only / Country only).
    """
    profile = load_profile()
    analyzed = []
    for job in jobs:
        result = analyze_job(job, profile)
        if not result["is_disqualified"] and result["score"] >= min_score:
            analyzed.append(result)
            
    analyzed.sort(key=lambda x: x["score"], reverse=True)
    return analyzed

if __name__ == "__main__":
    from fetcher import fetch_all_jobs
    jobs = fetch_all_jobs()
    ranked = rank_jobs(jobs, min_score=20)
    print(f"Top Matched Roles (Strict Junior, AI-Assisted, Global): {len(ranked)}")
    for i, j in enumerate(ranked[:15], 1):
        em = f" [Email: {j['apply_email']}]" if j.get('apply_email') else ""
        print(f"{i}. [{j['score']}%] {j['title']} @ {j['company']} ({j['location']}){em}")
