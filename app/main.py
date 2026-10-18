import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fastapi import FastAPI, BackgroundTasks, HTTPException
import os

app = FastAPI(title="HR OSINT Security Vetting Toolkit")

RECRUITMENT_EMAIL = os.getenv("RECRUITMENT_EMAIL", "recruitment@company.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def send_email_with_pdf(recipient: str, candidate_name: str, pdf_filename: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"[WARN] SMTP credentials not set. Skipping email dispatch for {candidate_name}.")
        return

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = recipient
    msg['Subject'] = f"Security Clearance Audit Report: {candidate_name}"

    body = f"Attached is the automated OSINT social media vetting dossier for candidate {candidate_name}."
    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_filename, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(pdf_filename))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_filename)}"'
        msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

@app.post("/api/v1/webhook/google-form")
async def handle_google_form_submission(data: dict, background_tasks: BackgroundTasks):
    if not data.get("consent_given"):
        raise HTTPException(status_code=400, detail="Candidate consent not granted.")

    candidate_name = data.get("full_name", "Candidate")
    safe_name = "".join(c if c.isalnum() else "_" for c in candidate_name).lower()
    pdf_filename = f"/app/reports/vetting_{safe_name}.pdf"

    handles = data.get("handles", {})
    
    # Simulated audit results (hook your scraper/API calls here)
    audit_results = [
        {"platform": "Twitter/X", "handle": handles.get("twitter", "N/A"), "risk_score": 0, "flagged_posts": []},
        {"platform": "LinkedIn", "handle": handles.get("linkedin", "N/A"), "risk_score": 0, "flagged_posts": []}
    ]

    from app.engines.reporter import AuditPDFReport
    reporter = AuditPDFReport(pdf_filename)
    reporter.build_report(data, audit_results)

    background_tasks.add_task(send_email_with_pdf, RECRUITMENT_EMAIL, candidate_name, pdf_filename)

    return {"status": "Processing complete", "report_generated": pdf_filename}
