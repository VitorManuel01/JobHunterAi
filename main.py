"""
Job Hunter AI - Main CLI Controller
Automated remote job discovery, matching, and application generator for Vitor Manuel.
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any

import sys

# Force UTF-8 on Windows terminal if available
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fetcher import fetch_all_jobs, CACHE_FILE
from matcher import rank_jobs, load_profile
from generator import generate_cover_letter, generate_ats_answers
from autofill import auto_fill_job_application
from email_sender import generate_email_application

APP_DIR = os.path.dirname(__file__)
APPLICATIONS_DIR = os.path.join(APP_DIR, "applications")

def print_header():
    print("=" * 70)
    print("       JOB HUNTER AI - Remote Dev & AI-Assisted Job Engine")
    print("=" * 70)

def cmd_search(args):
    print_header()
    jobs = fetch_all_jobs(force_refresh=args.refresh)
    min_score = 1 if getattr(args, 'email', False) else args.min_score
    ranked = rank_jobs(jobs, min_score=min_score)

    if getattr(args, 'brasil', False):
        ranked = [j for j in ranked if j.get('is_brazilian')]
        print(f"\n[+] Total Available Jobs Scanned: {len(jobs)}")
        print(f"[+] Brazilian Tech Matches Found (CLT/PJ/Remoto): {len(ranked)}\n")
    elif getattr(args, 'email', False):
        ranked = [j for j in ranked if j.get('apply_email')]
        print(f"\n[+] Total Available Jobs Scanned: {len(jobs)}")
        print(f"[+] Direct Email Application Matches Found: {len(ranked)}\n")
    else:
        print(f"\n[+] Total Available Jobs Scanned: {len(jobs)}")
        print(f"[+] High-Compatibility Matches Found: {len(ranked)} (Score >= {args.min_score}%)\n")
    
    print(f"{'#':<3} | {'SCORE':<5} | {'TITLE':<38} | {'COMPANY':<18} | {'REGION':<8} | {'SOURCE'}")
    print("-" * 88)
    
    limit = args.limit if args.limit else len(ranked)
    for idx, j in enumerate(ranked[:limit], 1):
        title = j['title'][:36] + ".." if len(j['title']) > 38 else j['title']
        company = j['company'][:16] + ".." if len(j['company']) > 18 else j['company']
        region = "🇧🇷 BR" if j.get('is_brazilian') else "🌐 Global"
        print(f"{idx:<3} | {j['score']:>3}%  | {title:<38} | {company:<18} | {region:<8} | {j['source']}")
        print(f"    |-- ID: {j['job_id']} | Proj: {j['recommended_project']['name']}")
        if j.get('apply_email'):
            print(f"        Email: {j['apply_email']}")
        print(f"        URL: {j['url']}")
        print()

def cmd_view(args):
    print_header()
    jobs = fetch_all_jobs()
    job = next((j for j in jobs if j["id"] == args.job_id), None)
    if not job:
        print(f"[!] Job with ID '{args.job_id}' not found.")
        return

    profile = load_profile()
    from matcher import analyze_job
    match_info = analyze_job(job, profile)

    print(f"TITLE:       {job['title']}")
    print(f"COMPANY:     {job['company']}")
    print(f"SOURCE:      {job['source']}")
    print(f"LOCATION:    {job['location']}")
    print(f"URL:         {job['url']}")
    print(f"MATCH SCORE: {match_info['score']}%")
    print(f"BEST PROJ:   {match_info['recommended_project']['name']}")
    print(f"TAGS:        {', '.join(job.get('tags', []))}")
    print("\n--- DESCRIPTION EXCERPT ---")
    desc = job.get('description', '')
    print(desc[:800] + ("..." if len(desc) > 800 else ""))
    print("-" * 70)

def cmd_apply(args):
    print_header()
    jobs = fetch_all_jobs()
    job = next((j for j in jobs if j["id"] == args.job_id), None)
    if not job:
        print(f"[!] Job with ID '{args.job_id}' not found.")
        return

    profile = load_profile()
    from matcher import analyze_job
    match_info = analyze_job(job, profile)

    cl = generate_cover_letter(match_info, job)
    ats = generate_ats_answers(match_info, job)

    print(f"\n[+] Generated Application Kit for: {job['title']} @ {job['company']}")
    print("=" * 70)
    print("\n--- COVER LETTER ---\n")
    print(cl)
    print("\n--- ATS PRE-FILLED FORM ANSWERS ---\n")
    for key, val in ats.items():
        print(f"[{key.upper()}]:\n{val}\n")

    os.makedirs(APPLICATIONS_DIR, exist_ok=True)
    out_file = os.path.join(APPLICATIONS_DIR, f"{args.job_id}_kit.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# Application Kit: {job['title']} at {job['company']}\n")
        f.write(f"- **URL**: {job['url']}\n")
        f.write(f"- **Match Score**: {match_info['score']}%\n")
        f.write(f"- **Recommended Project**: {match_info['recommended_project']['name']} ({match_info['recommended_project']['url']})\n\n")
        f.write("## 1. Tailored Cover Letter\n```\n" + cl + "\n```\n\n")
        f.write("## 2. Pre-Filled ATS Answers\n")
        for k, v in ats.items():
            f.write(f"### {k.replace('_', ' ').title()}\n{v}\n\n")

    print(f"[+] Saved application kit to: {out_file}")

def cmd_autofill(args):
    print_header()
    target_url = args.target
    cover_letter = ""

    # Check if target is a known job_id or a direct URL
    jobs = fetch_all_jobs()
    job = next((j for j in jobs if j["id"] == args.target), None)
    
    if job:
        target_url = job["url"]
        profile = load_profile()
        from matcher import analyze_job
        match_info = analyze_job(job, profile)
        cover_letter = generate_cover_letter(match_info, job)
        print(f"[+] Found job posting: {job['title']} at {job['company']}")
    else:
        print(f"[+] Target recognized as direct URL: {target_url}")

    # Resume PDF check in current folder if available
    resume_pdf = os.path.join(APP_DIR, "resume.pdf")
    if not os.path.exists(resume_pdf):
        resume_pdf = None

    auto_fill_job_application(target_url, cover_letter_text=cover_letter, resume_pdf_path=resume_pdf)

def cmd_email(args):
    print_header()
    jobs = fetch_all_jobs()
    job = next((j for j in jobs if j["id"] == args.job_id), None)
    if not job:
        print(f"[!] Job with ID '{args.job_id}' not found.")
        return

    profile = load_profile()
    from matcher import analyze_job
    match_info = analyze_job(job, profile)

    apply_email = job.get("apply_email")
    if not apply_email:
        print(f"[!] Note: No direct application email found in this posting's metadata.")
        print(f"    You can apply via browser with: python main.py autofill {job['id']}")
        return

    draft = generate_email_application(match_info, job)

    print(f"\n[+] Generated Direct Email Application for: {job['title']} @ {job['company']}")
    print("=" * 70)
    print(f"TO:          {draft['to']}")
    print(f"SUBJECT:     {draft['subject']}")
    print(f"ATTACHMENTS: {', '.join([os.path.basename(a) for a in draft['attachments']])}")
    print("\n--- EMAIL BODY ---\n")
    print(draft["body_text"])
    print("=" * 70)

    os.makedirs(APPLICATIONS_DIR, exist_ok=True)
    out_file = os.path.join(APPLICATIONS_DIR, f"{args.job_id}_email_draft.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# Direct Email Application: {job['title']} at {job['company']}\n")
        f.write(f"- **To**: {draft['to']}\n")
        f.write(f"- **Subject**: {draft['subject']}\n")
        f.write(f"- **Attachments**: {', '.join([os.path.basename(a) for a in draft['attachments']])}\n\n")
        f.write(f"```\n{draft['body_text']}\n```\n")

    print(f"[+] Saved email draft to: {out_file}")
    print(f"\n[🔗 1-Click Compose Links]")
    print(f"• Outlook Web: {draft['outlook_web_url']}")
    print(f"• Gmail Web:   {draft['gmail_web_url']}")
    print(f"• Mailto Link: {draft['mailto_url']}")

def cmd_report(args):
    print_header()
    jobs = fetch_all_jobs(force_refresh=args.refresh)
    ranked = rank_jobs(jobs, min_score=args.min_score)

    report_path = os.path.join(APP_DIR, "MATCHING_JOBS_REPORT.md")
    
    br_matches = [j for j in ranked if j.get('is_brazilian')][:12]
    intl_matches = [j for j in ranked if not j.get('is_brazilian')][:12]
    email_matches = [j for j in ranked if j.get('apply_email')][:10]

    profile_name = profile.get("name", "Developer")
    flagship = profile.get("portfolio_projects", [{}])[0]
    flagship_str = f"[{flagship.get('name', 'Portfolio')} — {flagship.get('description', '')}]({flagship.get('url', '#')})" if flagship else "See profile.json"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 🎯 Top Remote & Regional Job Matches for {profile_name}\n\n")
        f.write("Scored for Junior / AI-Assisted Software Engineering, Java/Spring, Flutter, Python, and SQL.\n")
        f.write("- **Currículo Nacional (Português - 1 página A4 ATS)**: `curriculo.pdf`\n")
        f.write("- **International Resume (English - 1 page US Letter ATS)**: `resume.pdf`\n")
        f.write(f"- **Flagship Showcase Project**: {flagship_str}\n\n")

        # Section 1: Brazilian Opportunities
        f.write("## 🇧🇷 1. Vagas Nacionais (Brasil — CLT / PJ / Remoto)\n\n")
        f.write("| Score | Posição | Empresa | Modalidade / Local | Projeto Recomendado | Ação |\n")
        f.write("| :---: | :--- | :--- | :--- | :--- | :--- |\n")
        for j in br_matches:
            email_tag = f" ✉️ `{j['apply_email']}`" if j.get('apply_email') else ""
            f.write(f"| **{j['score']}%** | [{j['title']}]({j['url']}){email_tag} | **{j['company']}** | {j['location']} | `{j['recommended_project']['name']}` | `python main.py apply {j['job_id']}` |\n")

        # Section 2: International Opportunities
        f.write("\n\n---\n")
        f.write("## 🌐 2. International Remote Opportunities (Global B2B Contractor — USD / EUR)\n\n")
        f.write("| Score | Position | Company | Location | Best Project | Action |\n")
        f.write("| :---: | :--- | :--- | :--- | :--- | :--- |\n")
        for j in intl_matches:
            email_tag = f" ✉️ `{j['apply_email']}`" if j.get('apply_email') else ""
            f.write(f"| **{j['score']}%** | [{j['title']}]({j['url']}){email_tag} | **{j['company']}** | {j['location']} | `{j['recommended_project']['name']}` | `python main.py apply {j['job_id']}` |\n")

        # Section 3: Direct Email Outreach
        if email_matches:
            f.write("\n\n---\n")
            f.write("## ✉️ 3. Direct Email Application Matches (Zero Intermediate ATS)\n\n")
            f.write("| Score | Posição / Role | Empresa | Destinatário de E-mail | Anexo Automático | Comando de Disparo |\n")
            f.write("| :---: | :--- | :--- | :--- | :--- | :--- |\n")
            for j in email_matches:
                att = "curriculo.pdf" if j.get('is_brazilian') else "resume.pdf"
                f.write(f"| **{j['score']}%** | [{j['title']}]({j['url']}) | **{j['company']}** | `{j['apply_email']}` | `{att}` | `python main.py email {j['job_id']}` |\n")

        f.write("\n\n---\n")
        f.write("## Detailed Job Pitch & Alignment Guides\n\n")
        for idx, j in enumerate(br_matches[:5] + intl_matches[:5], 1):
            lang = "Português (curriculo.pdf)" if j.get('is_brazilian') else "English (resume.pdf)"
            f.write(f"### {idx}. {j['title']} — {j['company']} ({j['score']}% Match)\n")
            f.write(f"- **Job Link**: [Open Posting]({j['url']})\n")
            f.write(f"- **Source**: {j['source']} | **Location**: {j['location']}\n")
            f.write(f"- **Idioma da Candidatura**: {lang}\n")
            f.write(f"- **Keywords Matched**: `{', '.join(j['matched_keywords'])}`\n")
            f.write(f"- **Pitch Angle**: Highlight **{j['recommended_project']['name']}** ({j['recommended_project']['url']})\n")
            f.write(f"- **CLI Command to Generate Kit**: `python main.py apply {j['job_id']}`\n\n")

    print(f"[+] Generated markdown report at: {report_path}")
    print(f"[+] Exported {len(br_matches)} Brazilian jobs and {len(intl_matches)} International jobs.")

def main():
    parser = argparse.ArgumentParser(description="Job Hunter AI: Discover and apply to remote dev jobs.")
    subparsers = parser.add_subparsers(dest="command")

    # Search command
    p_search = subparsers.add_parser("search", help="Search and rank live remote jobs")
    p_search.add_argument("--refresh", action="store_true", help="Force refresh job feeds from APIs")
    p_search.add_argument("--min-score", type=int, default=20, help="Minimum match score percentage (default: 20)")
    p_search.add_argument("--limit", type=int, default=15, help="Number of jobs to display (default: 15)")
    p_search.add_argument("--email", "-e", action="store_true", help="Filter strictly for jobs that accept applications via direct email")
    p_search.add_argument("--brasil", "-b", action="store_true", help="Filter strictly for Brazilian tech jobs (CLT / PJ / Remoto)")

    # View command
    p_view = subparsers.add_parser("view", help="View full job details")
    p_view.add_argument("job_id", type=str, help="Job ID from search results")

    # Apply command
    p_apply = subparsers.add_parser("apply", help="Generate tailored cover letter and ATS form answers")
    p_apply.add_argument("job_id", type=str, help="Job ID to apply to")

    # Report command
    p_report = subparsers.add_parser("report", help="Export top matches to a clean Markdown report")
    p_report.add_argument("--refresh", action="store_true", help="Force refresh job feeds from APIs")
    p_report.add_argument("--min-score", type=int, default=20, help="Minimum match score percentage")
    p_report.add_argument("--limit", type=int, default=15, help="Number of matches to include")

    # Autofill command (Playwright browser)
    p_autofill = subparsers.add_parser("autofill", help="Open browser and auto-fill the application form")
    p_autofill.add_argument("target", type=str, help="Job ID (e.g. remotive_2091158) or a direct URL")

    # Email command (Direct email application)
    p_email = subparsers.add_parser("email", help="Generate an email application draft with 1-click webmail links")
    p_email.add_argument("job_id", type=str, help="Job ID to apply by email")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "view":
        cmd_view(args)
    elif args.command == "apply":
        cmd_apply(args)
    elif args.command == "autofill":
        cmd_autofill(args)
    elif args.command == "email":
        cmd_email(args)
    elif args.command == "report":
        cmd_report(args)
    else:
        # Default behavior: run search
        class DefaultArgs:
            refresh = False
            min_score = 20
            limit = 10
        cmd_search(DefaultArgs())

if __name__ == "__main__":
    main()
