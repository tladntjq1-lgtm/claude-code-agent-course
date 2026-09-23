import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv


def send_slack(text, env_path=".env"):
    load_dotenv(env_path, override=True)
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False
    res = requests.post(webhook_url, json={"text": text})
    return res.status_code == 200 and res.text == "ok"


def send_email(subject, body, env_path=".env", to_addr=None):
    load_dotenv(env_path, override=True)
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    to_addr = to_addr or gmail_user
    if not gmail_user or not gmail_app_password:
        return False

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_app_password)
            server.sendmail(gmail_user, to_addr, msg.as_string())
        return True
    except smtplib.SMTPException:
        return False
