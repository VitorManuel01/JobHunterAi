"""
Email Application Automation Module
Handles:
1. Drafting personalized email applications with subject, body, and attachments (resume.pdf).
2. Direct SMTP delivery (Hotmail/Outlook, Gmail, or custom SMTP).
3. Fallback Mailto launcher for 1-click webmail/client drafting.
"""

import os
import smtplib
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List, Optional

from matcher import load_profile

APP_DIR = os.path.dirname(__file__)
ENV_FILE = os.path.join(APP_DIR, ".env")

def load_env() -> Dict[str, str]:
    """Loads environment variables from .env if present."""
    config = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().strip("'\"")
    return config

def is_brazilian_job(job_match: Dict[str, Any], raw_job: Dict[str, Any]) -> bool:
    """Detects whether a job is based in Brazil or the Brazilian tech market."""
    if job_match.get("is_brazilian"):
        return True
    loc = (job_match.get("location") or raw_job.get("location") or "").lower()
    source = (job_match.get("source") or raw_job.get("source") or "").lower()
    desc = (job_match.get("description") or raw_job.get("description") or "").lower()
    tags = [t.lower() for t in (job_match.get("tags") or raw_job.get("tags") or [])]
    
    if any(k in loc for k in [
        "brasil", "brazil", "são paulo", "sao paulo", "rio de janeiro", "curitiba",
        "belo horizonte", "salvador", "florianópolis", "florianopolis", "porto alegre",
        "recife", "campinas", "remoto brasil"
    ]):
        return True
    if any(t in ["brasil", "brazil", "portuguese", "nacional", "vagas-br", "remoto brasil"] for t in tags):
        return True
    if "github (backend-br" in source or "github (frontendbr" in source:
        return True
    if any(w in desc for w in ["clt", "pj", "remoto brasil", "salvador", "são paulo", "benefícios", "horário flexível", "contratação clt", "contratação pj"]):
        return True
    return False

def generate_email_application(job_match: Dict[str, Any], raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a high-converting cold email application for a job.
    Routes language and resume attachment automatically:
    - Brazilian jobs: Portuguese email + attaches curriculo.pdf
    - International jobs: English email + attaches resume.pdf
    """
    profile = load_profile()
    recipient_email = raw_job.get("apply_email", "")
    proj = job_match.get("recommended_project", profile["portfolio_projects"][0])
    is_brazil = is_brazilian_job(job_match, raw_job)

    attachments = []
    
    if is_brazil:
        company = job_match.get("company", "Equipe de Engenharia")
        title = job_match.get("title", "Desenvolvedor de Software")
        subject = f"Candidatura: {title} — {profile['name']} (Engenheiro de Software & Sistemas com IA)"
        
        body_text = f"""Prezada equipe de recrutamento da {company},

Escrevo para manifestar meu grande entusiasmo pela oportunidade de {title}. Sou Engenheiro de Software especializado no desenvolvimento backend e de sistemas com engenharia acelerada por IA, entregando soluções robustas e com alta velocidade.

Recentemente, arquitetei e lancei o {proj['name']} ({', '.join(proj['tech_stack'])}):
• {proj['description']}
• {proj['highlights']}
• Código e Arquitetura no GitHub: {proj['url']}

Principais diferenciais técnicos que agrego à equipe:
1. Desenvolvimento de Software Assistido por IA: Estruturo fluxos com múltiplos harnesses de IA em paralelo operando com protocolos de contexto compartilhado e suítes de testes automatizados.
2. Base Sólida em Engenharia & Sistemas: Domínio prático de {', '.join(profile.get('skills', {}).get('languages', ['Java', 'Python', 'SQL', 'Flutter']))} e bancos de dados relacionais.
3. Disponibilidade e Flexibilidade: Residente em {profile['contact']['location']}, disponibilidade imediata para início em modelo Remoto ou Híbrido, tanto via CLT quanto PJ.

Segue anexo meu currículo técnico de 1 página otimizado para ATS (curriculo.pdf). Coloco-me à disposição para conversar sobre como minha velocidade prática e rigor técnico podem acelerar os objetivos da {company}.

Atenciosamente,

{profile['name']}
{profile.get('headline', 'Engenheiro de Software | Desenvolvimento Assistido por IA')}
Email: {profile['contact']['email']} | Telefone: {profile['contact']['phone']}
GitHub: {profile['contact']['github']}
LinkedIn: {profile['contact']['linkedin']}
"""

        body_html = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1e293b;">
<p>Prezada equipe de recrutamento da <strong>{company}</strong>,</p>

<p>Escrevo para manifestar meu grande entusiasmo pela oportunidade de <strong>{title}</strong>. Sou Engenheiro de Software focado no desenvolvimento backend e de sistemas com engenharia acelerada por IA, entregando soluções robustas e com alta velocidade.</p>

<p>Recentemente, arquitetei e lancei o <strong><a href="{proj['url']}" style="color: #2563eb; text-decoration: none;">{proj['name']}</a></strong> ({', '.join(proj['tech_stack'])}):</p>
<ul>
  <li>{proj['description']}</li>
  <li>{proj['highlights']}</li>
  <li>Repositório GitHub: <a href="{proj['url']}">{proj['url']}</a></li>
</ul>

<p><strong>Diferenciais Principais:</strong></p>
<ol>
  <li><strong>Desenvolvimento de Software Assistido por IA:</strong> Fluxo com ferramentas modernas de engenharia assistida por IA com validação contínua e testes automatizados.</li>
  <li><strong>Base Sólida em Engenharia & Sistemas:</strong> Prática com {', '.join(profile.get('skills', {}).get('languages', ['Java', 'Python', 'SQL', 'Flutter']))} e bancos relacionais.</li>
  <li><strong>Disponibilidade Imediata:</strong> Residente no Brasil ({profile['contact']['location']}), elegível e disponível imediatamente para contratação CLT ou PJ (Remoto ou Híbrido).</li>
</ol>

<p>Segue anexo meu currículo técnico de 1 página (PDF). Coloco-me à disposição para conversar sobre como minhas habilidades práticas podem agregar valor imediato à {company}.</p>

<p>Atenciosamente,<br>
<strong>{profile['name']}</strong><br>
<em>{profile.get('headline', 'Engenheiro de Software | Desenvolvimento Assistido por IA')}</em><br>
GitHub: <a href="{profile['contact']['github']}">{profile['contact']['github']}</a> &bull; LinkedIn: <a href="{profile['contact']['linkedin']}">{profile['contact']['linkedin']}</a><br>
{profile['contact']['email']} &bull; {profile['contact']['phone']}
</p>
</div>"""

        curriculo_pdf = os.path.join(APP_DIR, "curriculo.pdf")
        if os.path.exists(curriculo_pdf):
            attachments.append(curriculo_pdf)
            attachment_name = "curriculo.pdf (Currículo Nacional ATS)"
        else:
            resume_pdf = os.path.join(APP_DIR, "resume.pdf")
            if os.path.exists(resume_pdf):
                attachments.append(resume_pdf)
            attachment_name = "resume.pdf (Currículo ATS)"

    else:
        company = job_match.get("company", "the Team")
        title = job_match.get("title", "Software Engineer")
        subject = f"Application: {title} — {profile['name']} (AI-Assisted Software Engineer)"
        
        body_text = f"""Dear Hiring Team at {company},

I am writing to express my strong enthusiasm for the {title} position. As a Software Engineer specializing in backend systems and AI-assisted software engineering, I deliver robust, high-velocity code with engineering rigor.

In my recent work, I architected and shipped {proj['name']} ({', '.join(proj['tech_stack'])}):
• {proj['description']}
• {proj['highlights']}
• Source Code & Architecture: {proj['url']}

My core strengths include:
1. AI-Assisted Software Engineering: Pioneered multi-agent AI development workflows running with shared context and automated test suites.
2. Full-Stack Foundation: Hands-on experience across {', '.join(profile.get('skills', {}).get('languages', ['Java', 'Python', 'SQL', 'Flutter']))} and relational database systems.
3. Availability & Remote Fluency: Fluent in English, based in Brazil ({profile['contact']['location']}), available immediately for full-time remote contractor (B2B) engagement with flexible timezone overlap.

Please find my 1-page international technical resume attached (PDF). I would welcome the opportunity to discuss how my velocity and practical engineering experience can immediately accelerate your product roadmap.

Best regards,

{profile['name']}
{profile.get('headline', 'Software Engineer | AI-Assisted Software Engineer')}
Email: {profile['contact']['email']} | Phone: {profile['contact']['phone']}
GitHub: {profile['contact']['github']}
LinkedIn: {profile['contact']['linkedin']}
"""

        body_html = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1e293b;">
<p>Dear Hiring Team at <strong>{company}</strong>,</p>

<p>I am writing to express my strong enthusiasm for the <strong>{title}</strong> position. As a Software Engineer specializing in backend systems and AI-assisted software engineering, I deliver robust, high-velocity code with engineering rigor.</p>

<p>In my recent work, I architected and shipped <strong><a href="{proj['url']}" style="color: #2563eb; text-decoration: none;">{proj['name']}</a></strong> ({', '.join(proj['tech_stack'])}):</p>
<ul>
  <li>{proj['description']}</li>
  <li>{proj['highlights']}</li>
  <li>GitHub Repository: <a href="{proj['url']}">{proj['url']}</a></li>
</ul>

<p><strong>Key Highlights:</strong></p>
<ol>
  <li><strong>AI-Assisted Software Engineering:</strong> Pioneered multi-agent AI development workflows with automated test verification.</li>
  <li><strong>Full-Stack Foundation:</strong> Hands-on experience across {', '.join(profile.get('skills', {}).get('languages', ['Java', 'Python', 'SQL', 'Flutter']))} and relational database systems.</li>
  <li><strong>Availability:</strong> Fluent in English, based in Brazil ({profile['contact']['location']}), immediately available for remote B2B / Contractor engagement.</li>
</ol>

<p>Please find my 1-page international technical resume attached (PDF). I would welcome the opportunity to discuss how my velocity and practical engineering experience can immediately accelerate your product roadmap.</p>

<p>Best regards,<br>
<strong>{profile['name']}</strong><br>
<em>{profile.get('headline', 'Software Engineer | AI-Assisted Software Engineer')}</em><br>
GitHub: <a href="{profile['contact']['github']}">{profile['contact']['github']}</a> &bull; LinkedIn: <a href="{profile['contact']['linkedin']}">{profile['contact']['linkedin']}</a><br>
{profile['contact']['email']} &bull; {profile['contact']['phone']}
</p>
</div>"""

        resume_pdf = os.path.join(APP_DIR, "resume.pdf")
        if os.path.exists(resume_pdf):
            attachments.append(resume_pdf)
        attachment_name = "resume.pdf (Currículo Internacional ATS)"

    # Direct Webmail compose URLs (Using quote_via=urllib.parse.quote so spaces become %20 instead of +)
    params_mailto = {
        "subject": subject,
        "body": body_text
    }
    mailto_url = f"mailto:{recipient_email}?" + urllib.parse.urlencode(params_mailto, quote_via=urllib.parse.quote)
    
    # Outlook Web direct compose deeplink
    params_outlook = {
        "to": recipient_email,
        "subject": subject,
        "body": body_text
    }
    outlook_web_url = "https://outlook.live.com/mail/deeplink/compose?" + urllib.parse.urlencode(params_outlook, quote_via=urllib.parse.quote)

    # Gmail Web direct compose URL
    params_gmail = {
        "view": "cm",
        "fs": "1",
        "to": recipient_email,
        "su": subject,
        "body": body_text
    }
    gmail_web_url = "https://mail.google.com/mail/?" + urllib.parse.urlencode(params_gmail, quote_via=urllib.parse.quote)

    return {
        "to": recipient_email,
        "subject": subject,
        "body_text": body_text,
        "body_html": body_html,
        "attachments": attachments,
        "attachment_name": attachment_name,
        "is_brazilian": is_brazil,
        "mailto_url": mailto_url,
        "outlook_web_url": outlook_web_url,
        "gmail_web_url": gmail_web_url
    }

def send_email_smtp(to_email: str, subject: str, body_text: str, body_html: str, attachment_paths: List[str]) -> Dict[str, Any]:
    """
    Sends email via SMTP (Hotmail/Outlook, Gmail, etc.) using credentials from .env.
    """
    env = load_env()
    profile = load_profile()
    
    sender_email = env.get("SMTP_USER") or profile["contact"]["email"]
    sender_password = env.get("SMTP_PASSWORD") or env.get("EMAIL_PASSWORD")
    smtp_host = env.get("SMTP_HOST", "smtp.office365.com")
    smtp_port = int(env.get("SMTP_PORT", 587))

    if not sender_password:
        return {
            "status": "needs_config",
            "message": "Configuração SMTP necessária para envio 100% autônomo. Configure EMAIL_PASSWORD no arquivo .env."
        }

    try:
        msg = MIMEMultipart("mixed")
        msg["From"] = f"{profile['name']} <{sender_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        # Create alternative part for plain text + html
        alt_part = MIMEMultipart("alternative")
        alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
        if body_html:
            alt_part.attach(MIMEText(body_html, "html", "utf-8"))
        msg.attach(alt_part)

        # Attach PDF files
        for path in attachment_paths:
            if os.path.exists(path):
                filename = os.path.basename(path)
                with open(path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
                msg.attach(part)

        # Connect to SMTP server
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [to_email], msg.as_string())
        server.quit()

        return {
            "status": "success",
            "message": f"E-mail de candidatura enviado com sucesso para {to_email} com {len(attachment_paths)} anexo(s)!"
        }

    except smtplib.SMTPAuthenticationError as e:
        err_str = str(e)
        if "535" in err_str and ("outlook" in smtp_host or "office365" in smtp_host or "live.com" in smtp_host):
            msg = (
                "A Microsoft encerrou o suporte a autenticação básica/senhas de aplicativo para SMTP em contas pessoais (@hotmail/@outlook) em 16/09/2024. "
                "Para enviar com 1 clique, use o botão 'Abrir no Outlook Web' ou configure um e-mail Gmail no .env com senha de aplicativo Google."
            )
        else:
            msg = f"Falha de autenticação SMTP ({err_str}). Verifique usuário e senha no .env."
        return {
            "status": "error",
            "message": msg
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro no envio SMTP: {e}"
        }

if __name__ == "__main__":
    prof = load_profile()
    draft = generate_email_application(
        {"company": "Askable", "title": "Software Engineer", "recommended_project": prof["portfolio_projects"][0]},
        {"apply_email": "jobs@askable.com"}
    )
    print("Email Subject:", draft["subject"])
    print("Attachments:", draft["attachments"])
    print("To:", draft["to"])
    print("Sample Body:\n", draft["body_text"][:300] + "...")
