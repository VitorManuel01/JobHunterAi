"""
Application Content Generator Module (Bilingual: English & Portuguese)
Generates high-converting, tailored cover letters, cold emails,
and pre-filled answers for standard ATS application forms.
"""

import json
import os
from typing import Dict, Any

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "profile.json")

def load_profile() -> Dict[str, Any]:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

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

def generate_cover_letter(job_match: Dict[str, Any], raw_job: Dict[str, Any]) -> str:
    """
    Generates a personalized, ATS-friendly cover letter.
    Emits Portuguese for Brazilian positions, and English for international positions.
    """
    profile = load_profile()
    proj = job_match.get("recommended_project", profile["portfolio_projects"][0])
    
    # BRAZILIAN POSITION (Portuguese)
    if is_brazilian_job(job_match, raw_job):
        company = job_match.get("company", "Equipe de Engenharia")
        title = job_match.get("title", "Desenvolvedor de Software")
        
        return f"""Prezada equipe de recrutamento da {company},

Escrevo para manifestar meu grande entusiasmo pela oportunidade de {title}. Como Desenvolvedor de Software focado no desenvolvimento backend e de sistemas com engenharia acelerada por IA, entrego soluções robustas, testadas e com alta velocidade de desenvolvimento.

O que me motivou nesta oportunidade na {company} é a possibilidade de gerar impacto técnico prático imediato. Recentemente, arquitetei e entreguei o **{proj['name']}**, sistema desenvolvido com {", ".join(proj['tech_stack'])}. {proj['description']} Neste projeto, {proj['highlights']}. O código-fonte, arquitetura e testes podem ser conferidos diretamente no meu GitHub: {proj['url']}

Principais diferenciais técnicos que agrego à equipe:
• **Desenvolvimento de Software Assistido por IA:** Além de prompts simples, estruturo fluxos com múltiplos harnesses de IA em paralelo (Claude Code, OpenAI/Codex, Antigravity) operando em Git worktrees isolados, com protocolos de memória compartilhada (AGENTS.md) e validação contínua por suítes de testes automatizados.
• **Base Sólida em Engenharia e Sistemas:** Formação técnica e superior em Análise e Desenvolvimento de Sistemas (SENAI CIMATEC), com domínio prático em Java (POO/Spring), Flutter/Dart, Python e bancos de dados relacionais (PostgreSQL/MySQL).
• **Velocidade de Execução com Qualidade:** Elevada cadência de implementação sem abrir mão de arquitetura limpa, legibilidade e cobertura de testes.
• **Disponibilidade e Flexibilidade:** Residente no Brasil (Salvador/BA, UTC-3), disponibilidade imediata para início em modelo Remoto ou Híbrido, tanto via contratação CLT quanto PJ.

Agradeço pela atenção e consideração. Coloco-me à disposição para uma conversa técnica sobre como minha velocidade prática e experiência em engenharia de software podem acelerar as entregas da {company}.

Atenciosamente,

{profile['name']}
{profile.get('headline', 'Desenvolvedor de Software | Engenharia de Software com IA')}
{profile['contact']['email']} | {profile['contact']['phone']}
GitHub: {profile['contact']['github']} | LinkedIn: {profile['contact']['linkedin']}
"""

    # INTERNATIONAL POSITION (English)
    company = job_match.get("company", "the Hiring Team")
    title = job_match.get("title", "Software Engineer")
    
    return f"""Dear Hiring Team at {company},

I am writing to express my strong enthusiasm for the {title} position. As a Software Engineer specializing in backend systems and AI-assisted software engineering, I deliver robust, high-velocity code with architectural discipline.

What caught my attention about this role at {company} is the opportunity to contribute immediately to your product pipeline. In my recent work, I built and shipped **{proj['name']}**, an application utilizing {", ".join(proj['tech_stack'])}. {proj['description']} For this project, {proj['highlights']}. You can inspect the source code directly on my GitHub: {proj['url']}

My core technical approach centers on modern engineering efficiency:
• **AI-Assisted Software Engineering:** Beyond simple prompting, I design multi-harness workflows where parallel AI agents (Claude Code, Codex, Antigravity) develop concurrently across isolated Git worktrees under shared memory protocols (AGENTS.md) and automated test verification.
• **Full-Stack & Systems Competency:** Solid foundation across Java (OOP), Flutter/Dart, Python, and relational databases (SQL/MySQL/PostgreSQL).
• **Velocity & Reliability:** High output speed powered by modern agentic tools without sacrificing code quality, architectural consistency, or test coverage.
• **Remote Collaboration:** Advanced English proficiency, clear asynchronous communication, and experience working across global timezones.

I am available for full-time remote contractor (B2B) engagement immediately, with flexible overlap for your working hours.

Thank you for your time and consideration. I would welcome the opportunity to discuss how my hands-on project experience and technical speed can add value to {company}.

Sincerely,

{profile['name']}
{profile['headline']}
{profile['contact']['email']} | {profile['contact']['phone']}
GitHub: {profile['contact']['github']} | LinkedIn: {profile['contact']['linkedin']}
"""

def generate_ats_answers(job_match: Dict[str, Any], raw_job: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates pre-filled answers for the most common ATS form questions (Ashby, Greenhouse, Lever).
    Emits Portuguese for Brazilian positions, and English for international positions.
    """
    profile = load_profile()
    proj = job_match.get("recommended_project", profile["portfolio_projects"][0])
    
    # BRAZILIAN POSITION (Portuguese)
    if is_brazilian_job(job_match, raw_job):
        return {
            "full_name": profile["name"],
            "email": profile["contact"]["email"],
            "phone": profile["contact"]["phone"],
            "location": f"{profile['contact']['location']} (Disponível Remoto / Híbrido - CLT ou PJ)",
            "linkedin": profile["contact"]["linkedin"],
            "github": profile["contact"]["github"],
            "portfolio": proj["url"],
            
            "why_company": (
                f"Admiro o protagonismo técnico e a cultura de produto da {job_match.get('company')}. "
                f"Minha experiência prática desenvolvendo sistemas completos como {proj['name']} somada ao meu fluxo de "
                f"engenharia acelerada por IA me permite aprender rapidamente, colaborar com rigor técnico e contribuir desde a primeira semana."
            ),
            
            "relevant_experience": (
                f"Possuo experiência prática construindo aplicações completas com {', '.join(proj['tech_stack'])}. "
                f"No projeto {proj['name']}, realizei a {proj['highlights'].lower()} "
                f"Combino fundamentos sólidos de engenharia de software (SENAI CIMATEC) com ferramentas modernas de desenvolvimento assistido por IA "
                f"para implementar código limpo, consistente e testado."
            ),
            
            "salary_expectations": (
                "Aberto a negociação com base na senioridade da vaga e modelo de contratação (CLT ou PJ). "
                "Meu foco prioritário está no aprendizado acelerado, no impacto técnico do projeto e na sinergia com a equipe."
            ),
            
            "notice_period": "Disponibilidade imediata para início (0 dias de aviso prévio).",
            "work_authorization": "Brasileiro nato, elegível para contratação imediata via CLT ou PJ (sem restrições ou pendências contratuais)."
        }

    # INTERNATIONAL POSITION (English)
    return {
        "full_name": profile["name"],
        "email": profile["contact"]["email"],
        "phone": profile["contact"]["phone"],
        "location": f"{profile['contact']['location']} (Remote B2B)",
        "linkedin": profile["contact"]["linkedin"],
        "github": profile["contact"]["github"],
        "portfolio": proj["url"],
        
        "why_company": (
            f"I am excited by {job_match.get('company')}'s focus on product quality and remote collaboration. "
            f"My hands-on experience shipping real-world apps like {proj['name']} and my AI-accelerated workflow "
            f"allow me to adapt quickly, write reliable code, and contribute to your team from day one."
        ),
        
        "relevant_experience": (
            f"I have practical experience building production-ready applications with {', '.join(proj['tech_stack'])}. "
            f"In my project {proj['name']}, I {proj['highlights'].lower()} "
            f"I combine solid CS fundamentals from SENAI CIMATEC with modern AI development tooling (Cursor, Claude) "
            f"to ship bug-free features rapidly."
        ),
        
        "salary_expectations": (
            f"Open to discussion based on role scope. For remote contractor (B2B) roles, "
            f"my target range is $18 - $25 USD / hour (or $2,800 - $3,500 USD / month), but my primary focus is "
            f"on impact, growth, and team alignment."
        ),
        
        "notice_period": "Immediately available (0 days notice).",
        "work_authorization": "Brazilian Citizen. Available to work internationally under B2B / Independent Contractor agreements (W-8BEN compliant)."
    }

if __name__ == "__main__":
    from fetcher import fetch_all_jobs
    from matcher import rank_jobs
    
    jobs = fetch_all_jobs()
    ranked = rank_jobs(jobs)
    if ranked:
        target = ranked[0]
        raw = next((j for j in jobs if j["id"] == target["job_id"]), {})
        cl = generate_cover_letter(target, raw)
        print("Generated Sample Cover Letter:\n")
        print(cl[:400] + "...\n[OK]")
