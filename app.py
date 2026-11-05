"""
Job Hunter AI - Web GUI Application (Flask)
Interactive graphical dashboard for browsing jobs, generating cover letters,
and launching Playwright autofill with 1 click.
"""

import json
import os
import threading
import webbrowser
from flask import Flask, render_template, jsonify, request

from fetcher import fetch_all_jobs
from matcher import rank_jobs, analyze_job, load_profile
from generator import generate_cover_letter, generate_ats_answers
from autofill import auto_fill_job_application
from email_sender import generate_email_application

APP_DIR = os.path.dirname(__file__)
app = Flask(__name__, template_folder=os.path.join(APP_DIR, "templates"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/profile", methods=["GET"])
def get_profile():
    return jsonify(load_profile())

@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    min_score = request.args.get("min_score", default=15, type=int)
    search_query = request.args.get("q", default="", type=str).lower().strip()
    tag_filter = request.args.get("tag", default="", type=str).lower().strip()

    # If filtering by email, lower min_score so all legitimate direct-contact jobs are displayed
    effective_min_score = 1 if tag_filter == "email" else min_score

    all_jobs = fetch_all_jobs(force_refresh=False)
    ranked = rank_jobs(all_jobs, min_score=effective_min_score)

    filtered = []
    for j in ranked:
        if search_query:
            text = f"{j['title']} {j['company']} {j['location']}".lower()
            if search_query not in text:
                continue
        if tag_filter:
            if tag_filter == 'email':
                if not j.get('accepts_email') and not j.get('apply_email'):
                    continue
            elif tag_filter == 'brasil':
                if not j.get('is_brazilian') and 'brasil' not in f"{j['title']} {' '.join(j.get('tags', []))} {j.get('location', '')}".lower():
                    continue
            else:
                tags_str = ' '.join(j.get('tags', []))
                text = f"{j['title']} {' '.join(j.get('matched_keywords', []))} {tags_str} {j.get('location', '')} {j.get('category', '')}".lower()
                if tag_filter not in text:
                    continue
        filtered.append(j)

    return jsonify({
        "total_scanned": len(all_jobs),
        "total_matches": len(filtered),
        "jobs": filtered
    })

@app.route("/api/jobs/refresh", methods=["POST"])
def refresh_jobs():
    all_jobs = fetch_all_jobs(force_refresh=True)
    ranked = rank_jobs(all_jobs, min_score=15)
    return jsonify({
        "status": "success",
        "total_scanned": len(all_jobs),
        "total_matches": len(ranked)
    })

@app.route("/api/jobs/<job_id>", methods=["GET"])
def get_job_detail(job_id):
    all_jobs = fetch_all_jobs(force_refresh=False)
    raw_job = next((j for j in all_jobs if j["id"] == job_id), None)
    if not raw_job:
        return jsonify({"error": "Job not found"}), 404

    profile = load_profile()
    match_info = analyze_job(raw_job, profile)
    cover_letter = generate_cover_letter(match_info, raw_job)
    ats_answers = generate_ats_answers(match_info, raw_job)

    return jsonify({
        "raw": raw_job,
        "match": match_info,
        "cover_letter": cover_letter,
        "ats_answers": ats_answers
    })

@app.route("/api/jobs/<job_id>/autofill", methods=["POST"])
def trigger_autofill(job_id):
    all_jobs = fetch_all_jobs(force_refresh=False)
    raw_job = next((j for j in all_jobs if j["id"] == job_id), None)
    if not raw_job:
        return jsonify({"error": "Job not found"}), 404

    profile = load_profile()
    match_info = analyze_job(raw_job, profile)
    cover_letter = generate_cover_letter(match_info, raw_job)
    
    if match_info.get("is_brazilian"):
        curriculo_pdf = os.path.join(APP_DIR, "curriculo.pdf")
        resume_pdf = curriculo_pdf if os.path.exists(curriculo_pdf) else os.path.join(APP_DIR, "resume.pdf")
    else:
        resume_pdf = os.path.join(APP_DIR, "resume.pdf")

    if not os.path.exists(resume_pdf):
        resume_pdf = None

    # Run Playwright in a background thread so web server stays responsive
    thread = threading.Thread(
        target=auto_fill_job_application,
        args=(raw_job["url"], cover_letter, resume_pdf),
        daemon=True
    )
    thread.start()

    return jsonify({
        "status": "launched",
        "message": f"Navegador aberto para {raw_job['title']} em {raw_job['company']}!"
    })

@app.route("/api/jobs/<job_id>/email", methods=["GET"])
def get_job_email_draft(job_id):
    all_jobs = fetch_all_jobs(force_refresh=False)
    raw_job = next((j for j in all_jobs if j["id"] == job_id), None)
    if not raw_job:
        return jsonify({"error": "Job not found"}), 404

    profile = load_profile()
    match_info = analyze_job(raw_job, profile)
    email_draft = generate_email_application(match_info, raw_job)
    return jsonify(email_draft)

def start_server(port=5000, open_browser=True):
    if open_browser:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host="127.0.0.1", port=port, debug=False)

if __name__ == "__main__":
    start_server()
