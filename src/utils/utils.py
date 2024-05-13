import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
import secrets
import hashlib


def send_register_email(receiver, message):
    sender = "prohanter34@yandex.ru"
    password = os.getenv("EMAIL_PASSWORD")
    msg = MIMEText(f'{message}', 'plain', 'utf-8')
    msg['Subject'] = Header('Регистрация в SCAM CASINO', 'utf-8')
    msg['From'] = sender
    msg['To'] = receiver

    server = smtplib.SMTP("smtp.yandex.ru", 587, timeout=100)

    try:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        return 0

    except Exception as _ex:
        return 1


def generate_verify_code():
    return secrets.randbelow(900000) + 100000


def get_hash(message: str):
    hash = hashlib.new("sha256")
    hash.update(message.encode())
    hashCode = hash.hexdigest()
    return hashCode

