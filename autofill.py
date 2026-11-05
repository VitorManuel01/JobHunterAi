"""
Browser Auto-Filler Module using Playwright (Production Grade & Multi-File Support)
Features:
1. Multi-File ATS Support (Recruitee, Teamtailor, Greenhouse, Lever, Ashby):
   - CV / Resume -> resume.pdf
   - Cover Letter File -> cover_letter.pdf (auto-generated)
   - Photo / Avatar -> photo.jpg/png (if present in project folder)
2. Smart ATS Question Matching (Salary, GitHub, Portfolio project, Notice period, Work Auth).
3. Aggregator Isolation: Never fills newsletter or modal inputs on job boards (Remotive, Arbeitnow, Jobicy).
4. Direct ATS Navigation: Automatically extracts the real external company application URL.
5. Multi-Tab & Iframe Engine: Follows popups, switches active tab, and supports embedded ATS iframes.
"""

import json
import os
import re
import sys
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

# Force UTF-8 encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

APP_DIR = os.path.dirname(__file__)
PROFILE_PATH = os.path.join(APP_DIR, "profile.json")

def load_profile() -> Dict[str, Any]:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Job aggregators where job cards/summaries are hosted (NOT the actual ATS)
AGGREGATOR_DOMAINS = [
    "remotive.com",
    "arbeitnow.com",
    "arbeitnow.ch",
    "arbeitnow.nl",
    "arbeitnow.co.uk",
    "jobicy.com"
]

# Unrelated inputs to NEVER touch
INPUT_BLACKLIST = [
    r"newsletter", r"subscribe", r"report", r"dead-link", r"deadlink",
    r"feedback", r"alert", r"search", r"filter", r"login", r"signin",
    r"password", r"promo", r"coupon", r"discount", r"query", r"modal"
]

# Unsafe buttons to NEVER click
BUTTON_EXCLUSIONS = [
    r"filter", r"search", r"cookie", r"accept", r"agree", r"terms",
    r"privacy", r"with linkedin", r"with indeed", r"sign in", r"log in",
    r"subscribe", r"newsletter", r"save job", r"bookmark", r"share",
    r"report", r"dead link", r"cancel", r"close", r"dismiss", r"apply promo"
]

def is_aggregator(url: str) -> bool:
    domain = urlparse(url).netloc.lower()
    return any(agg in domain for agg in AGGREGATOR_DOMAINS)

def is_input_blacklisted(element) -> bool:
    try:
        attrs = [
            element.get_attribute("id") or "",
            element.get_attribute("name") or "",
            element.get_attribute("class") or "",
            element.get_attribute("placeholder") or "",
            element.get_attribute("aria-label") or ""
        ]
        combined = " ".join(attrs).lower()
        for pat in INPUT_BLACKLIST:
            if re.search(pat, combined):
                return True
    except Exception:
        pass
    return False

def find_external_apply_url(page) -> Optional[str]:
    try:
        links = page.locator("a").all()
        for l in links:
            try:
                txt = l.inner_text().strip().lower()
                href = (l.get_attribute("href") or "").strip()
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue
                if any(re.search(pat, txt) for pat in BUTTON_EXCLUSIONS):
                    continue
                if any(p in txt for p in ["apply for this position", "apply for this job", "apply on company", "apply now"]):
                    if href.startswith("http") and not is_aggregator(href):
                        return href
                    if href.endswith("/apply") or "/apply" in href:
                        return href
            except Exception:
                continue
    except Exception:
        pass
    return None

def fill_input_safely(ctx, selector: str, value: str, label_name: str) -> bool:
    if not value:
        return False
    try:
        elements = ctx.locator(selector).all()
        for el in elements:
            if el.is_visible() and not is_input_blacklisted(el):
                el.scroll_into_view_if_needed(timeout=1000)
                el.click(timeout=1000)
                el.fill("")
                el.fill(value)
                print(f"  [+] Pre-filled {label_name}: {value[:35]}{'...' if len(value) > 35 else ''}")
                return True
    except Exception:
        pass
    return False

def create_cover_letter_pdf(cover_letter_text: str, browser) -> Optional[str]:
    """Generates a clean PDF version of the cover letter for platforms that require a file upload."""
    if not cover_letter_text:
        return None
    pdf_path = os.path.join(APP_DIR, "cover_letter.pdf")
    try:
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 25mm 20mm; font-size: 11pt; line-height: 1.5; color: #0f172a; }}
  pre {{ font-family: inherit; white-space: pre-wrap; word-wrap: break-word; }}
</style>
</head>
<body><pre>{cover_letter_text}</pre></body>
</html>"""
        temp_page = browser.new_page()
        temp_page.set_content(html)
        temp_page.pdf(path=pdf_path, format="A4", print_background=True)
        temp_page.close()
        return pdf_path
    except Exception as e:
        print(f"  [!] Notice creating cover_letter.pdf: {e}")
        return None

def handle_smart_file_uploads(ctx, resume_pdf: Optional[str], cover_letter_pdf: Optional[str]):
    """
    Intelligently handles multi-file ATS requirements:
    Differentiates between CV, Cover Letter, and Photo upload inputs.
    """
    try:
        file_inputs = ctx.locator("input[type='file']").all()
        if not file_inputs:
            return

        # Check for photo file in project directory (photo.jpg, photo.png, etc.)
        photo_path = None
        for ext in [".jpg", ".jpeg", ".png"]:
            candidate = os.path.join(APP_DIR, f"photo{ext}")
            if os.path.exists(candidate):
                photo_path = candidate
                break

        for fi in file_inputs:
            name = (fi.get_attribute("name") or "").lower()
            id_ = (fi.get_attribute("id") or "").lower()
            accept = (fi.get_attribute("accept") or "").lower()
            
            # Context text from surrounding container/label
            ctx_text = ""
            try:
                ctx_text = fi.evaluate("el => el.closest('div, label, fieldset')?.innerText || ''").lower()
            except Exception:
                pass

            combined = f"{name} {id_} {ctx_text}"

            # 1. Photo input
            if "photo" in combined or "avatar" in combined or (accept.startswith("image") and "pdf" not in accept):
                if photo_path and os.path.exists(photo_path):
                    fi.set_input_files(photo_path)
                    print(f"  [+] Attached Photo: {os.path.basename(photo_path)}")
                else:
                    print("  [i] Photo upload slot found (Optional — add 'photo.jpg' in project folder to auto-attach)")

            # 2. Cover Letter file input
            elif "cover" in combined or "letter" in combined or "motivation" in combined:
                if cover_letter_pdf and os.path.exists(cover_letter_pdf):
                    fi.set_input_files(cover_letter_pdf)
                    print(f"  [+] Attached Cover Letter: {os.path.basename(cover_letter_pdf)}")

            # 3. Resume / CV input
            elif "cv" in combined or "resume" in combined or "curriculum" in combined or len(file_inputs) == 1:
                if resume_pdf and os.path.exists(resume_pdf):
                    fi.set_input_files(resume_pdf)
                    print(f"  [+] Attached Resume/CV: {os.path.basename(resume_pdf)}")
            else:
                # Default fallback
                if resume_pdf and os.path.exists(resume_pdf):
                    fi.set_input_files(resume_pdf)
                    print(f"  [+] Attached Resume: {os.path.basename(resume_pdf)}")

    except Exception as e:
        print(f"  [!] File upload notice: {e}")

def handle_smart_open_questions(ctx, profile: Dict[str, Any]):
    """
    Answers common ATS open-ended questions (salary, portfolio, github, notice period).
    """
    try:
        inputs = ctx.locator("input[type='text'], textarea, input:not([type])").all()
        for ti in inputs:
            try:
                # Skip if already filled or blacklisted
                val = ti.input_value()
                if val or is_input_blacklisted(ti):
                    continue

                ctx_text = ti.evaluate("el => el.closest('div, label, fieldset')?.innerText || ''").lower()
                placeholder = (ti.get_attribute("placeholder") or "").lower()
                name = (ti.get_attribute("name") or "").lower()
                combined = f"{ctx_text} {placeholder} {name}"

                if any(w in combined for w in ["salary", "compensation", "hourly", "rate", "remuneration", "gehalt"]):
                    ti.fill("$20 - $25 USD / hour (or $3,000 USD / month remote B2B)")
                    print("  [+] Answered Open Question: Salary Expectations ($20 - $25 USD / hr)")

                elif any(w in combined for w in ["github", "personal site", "git repository"]):
                    ti.fill(profile["contact"]["github"])
                    print(f"  [+] Answered Open Question: GitHub URL ({profile['contact']['github']})")

                elif any(w in combined for w in ["application you built", "links/screenshots", "portfolio", "projects"]):
                    flagship = profile["portfolio_projects"][0]
                    ti.fill(f"{flagship['url']} — {flagship['name']}: {flagship['highlights']}")
                    print(f"  [+] Answered Open Question: Flagship Project ({flagship['name']})")

                elif "linkedin" in combined:
                    ti.fill(profile["contact"]["linkedin"])
                    print(f"  [+] Answered Open Question: LinkedIn URL")

                elif any(w in combined for w in ["notice", "availability", "start date", "how soon"]):
                    ti.fill("Immediately available (0 days notice)")
                    print("  [+] Answered Open Question: Notice Period (Immediate)")

                elif any(w in combined for w in ["contest", "olympiad", "chess", "rating"]):
                    ti.fill("No formal competitive math or chess ratings. My analytical focus is practical and applied: designing reliable software architecture, clean state machines, and parallel AI agent orchestration in C#/.NET as demonstrated in my FalloutRemake project.")
                    print("  [+] Answered Open Question: Programming/Math Contests & Chess (Option 3 Practical Pivot)")

                elif any(w in combined for w in ["authorization", "visa", "citizenship", "work permit"]):
                    ti.fill("Brazilian Citizen. Available for international B2B / Contractor agreements (W-8BEN compliant).")
                    print("  [+] Answered Open Question: Work Authorization")

            except Exception:
                continue
    except Exception:
        pass

def fill_application_form(page, profile: Dict[str, Any], cover_letter: str, resume_pdf: Optional[str], cover_letter_pdf: Optional[str]) -> bool:
    full_name = profile["name"]
    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    filled_any = False
    contexts = [page] + page.frames

    for ctx in contexts:
        try:
            # 1. Full Name / First & Last Name
            if fill_input_safely(ctx, "input[name*='name' i]:not([name*='first']):not([name*='last']):not([name*='user']):not([name*='company']), input[id='name']", full_name, "Full Name"):
                filled_any = True
            else:
                if fill_input_safely(ctx, "input[name*='first' i], input[id*='first' i], input[placeholder*='first' i]", first_name, "First Name"):
                    filled_any = True
                if fill_input_safely(ctx, "input[name*='last' i], input[id*='last' i], input[placeholder*='last' i]", last_name, "Last Name"):
                    filled_any = True

            # 2. Email
            if fill_input_safely(ctx, "input[type='email'], input[name='email'], input[id='email'], input[name*='email' i]", profile["contact"]["email"], "Email"):
                filled_any = True

            # 3. Phone
            if fill_input_safely(ctx, "input[type='tel'], input[name*='phone' i], input[name*='mobile' i], input[id='phone']", profile["contact"]["phone"], "Phone"):
                filled_any = True

            # 4. Location
            fill_input_safely(ctx, "input[name*='location' i], input[name*='city' i], input[id*='location' i]", profile["contact"]["location"], "Location")

            # 5. Social & Portfolio Links
            fill_input_safely(ctx, "input[name*='linkedin' i], input[id*='linkedin' i]", profile["contact"]["linkedin"], "LinkedIn")
            fill_input_safely(ctx, "input[name*='github' i], input[id*='github' i]", profile["contact"]["github"], "GitHub")

            # 6. Cover Letter Textarea (if field is a text area)
            if cover_letter:
                textareas = [
                    "textarea[name*='cover' i]",
                    "textarea[name*='letter' i]",
                    "textarea[id*='cover' i]",
                    "textarea[id*='letter' i]",
                    "textarea[placeholder*='cover' i]",
                    "textarea[placeholder*='note' i]"
                ]
                for ta in textareas:
                    if fill_input_safely(ctx, ta, cover_letter, "Cover Letter Text"):
                        filled_any = True
                        break

            # 7. Multi-File Uploads (CV vs Cover Letter vs Photo)
            handle_smart_file_uploads(ctx, resume_pdf, cover_letter_pdf)

            # 8. Open ATS Questions (Salary, Links, Notice, etc.)
            handle_smart_open_questions(ctx, profile)

        except Exception:
            continue

    return filled_any

def auto_fill_job_application(target_url: str, cover_letter_text: str = "", resume_pdf_path: Optional[str] = None):
    from playwright.sync_api import sync_playwright

    profile = load_profile()
    print(f"\n[*] Target URL: {target_url}")
    print("[*] Launching Chromium in Supervised Mode...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=70)
        context = browser.new_context(
            viewport={"width": 1366, "height": 920},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Generate cover_letter.pdf if cover letter text is available
        cover_letter_pdf = create_cover_letter_pdf(cover_letter_text, browser)

        page = context.new_page()

        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            active_page = page

            # 1. If this is an AGGREGATOR (Remotive, Arbeitnow, Jobicy):
            if is_aggregator(active_page.url):
                print(f"[*] Aggregator detected ({urlparse(active_page.url).netloc}). Finding real external apply link...")
                ext_url = find_external_apply_url(active_page)

                if ext_url:
                    print(f"[+] Found external ATS link: {ext_url}")
                    print("[*] Navigating directly to destination company application...")
                    active_page.goto(ext_url, wait_until="domcontentloaded", timeout=30000)
                    active_page.wait_for_timeout(2500)
                else:
                    print("[!] No direct external URL attribute found. Attempting safe click...")
                    for l in active_page.locator("a, button").all():
                        try:
                            txt = l.inner_text().strip().lower()
                            if ("apply for this position" in txt or "apply now" in txt) and not any(re.search(e, txt) for e in BUTTON_EXCLUSIONS):
                                href = l.get_attribute("href") or ""
                                if href and href != "#":
                                    l.click()
                                    active_page.wait_for_timeout(3000)
                                    break
                        except Exception:
                            continue

                if len(context.pages) > 1:
                    active_page = context.pages[-1]
                    print(f"[+] Switched to new application tab: {active_page.url}")
                    active_page.bring_to_front()
                    active_page.wait_for_timeout(2000)

            # 2. On the Real Company / ATS Page:
            # Check if there is an "Apply" button to reveal the form
            has_form_already = False
            for ctx in [active_page] + active_page.frames:
                try:
                    email_loc = ctx.locator("input[type='email']").first
                    if email_loc.count() > 0 and email_loc.is_visible():
                        has_form_already = True
                        break
                except Exception:
                    pass

            if not has_form_already:
                for btn in active_page.locator("button, a").all():
                    try:
                        txt = btn.inner_text().strip().lower()
                        if txt in ["apply", "apply now", "apply for this job", "apply for this role"] and not any(re.search(e, txt) for e in BUTTON_EXCLUSIONS):
                            print(f"[*] Clicking company Apply button: '{txt}'")
                            btn.click()
                            active_page.wait_for_timeout(2500)
                            break
                    except Exception:
                        continue

            # 3. Pre-fill Application Fields Safely
            print(f"\n[*] Pre-filling verified application form on: {urlparse(active_page.url).netloc}...")
            filled = fill_application_form(active_page, profile, cover_letter_text, resume_pdf_path, cover_letter_pdf)

            if filled:
                print("\n" + "=" * 70)
                print("  STATUS: FORMULÁRIO PREENCHIDO COM SUCESSO!")
                print("  O navegador está aberto na sua tela para conferência.")
                print("  1. Verifique os campos e arquivos anexados (CV, Cover Letter, Foto).")
                print("  2. Responda a qualquer pergunta específica da empresa.")
                print("  3. Clique em Submit quando estiver 100% satisfeito.")
                print("=" * 70)
            else:
                print("\n[!] Nenhum formulário padrão detectado automaticamente.")
                print("    A página da vaga está aberta na sua tela para preenchimento manual.")

            print("Pressione Enter neste terminal quando terminar para fechar o navegador...")
            try:
                input()
            except EOFError:
                active_page.wait_for_timeout(35000)

        except Exception as e:
            print(f"[!] Erro na automação: {e}")
            page.wait_for_timeout(15000)
        finally:
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        pdf = os.path.join(APP_DIR, "resume.pdf")
        if not os.path.exists(pdf):
            pdf = None
        auto_fill_job_application(target, cover_letter_text="AI-Assisted Software Engineer & Vibe Coder specializing in C#, Java, and Python.", resume_pdf_path=pdf)
    else:
        print("Usage: python autofill.py <url>")
