"""Send email alert on post success or failure."""
import os
import smtplib
from email.mime.text import MIMEText


def send_alert(subject: str, body: str):
    gmail   = os.getenv("GMAIL_ADDRESS", "")
    app_pwd = os.getenv("GMAIL_APP_PASSWORD", "")
    targets = [e.strip() for e in os.getenv("ALERT_EMAILS", "").split(",") if e.strip()]

    if not gmail or not app_pwd or not targets:
        print(f"[alert] {subject}")
        return

    msg          = MIMEText(body, "plain", "utf-8")
    msg["From"]  = gmail
    msg["To"]    = ", ".join(targets)
    msg["Subject"] = subject

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail, app_pwd)
            smtp.sendmail(gmail, targets, msg.as_string())
        print(f"[alert] Email sent: {subject}")
    except Exception as e:
        print(f"[alert] Email failed (non-fatal): {e}")
        print(f"[alert] {subject}")
