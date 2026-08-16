import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("SMTP_HOST", "smtp.gmail.com")
port = int(os.getenv("SMTP_PORT", 587))
user = os.getenv("SMTP_USER")
pwd = os.getenv("SMTP_PASSWORD")

print(f"Loaded User: '{user}'")
print(f"Loaded Password Length: {len(pwd) if pwd else 0} characters")

try:
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, pwd)
        print("\nSUCCESS: Gmail accepted your credentials!")
except Exception as e:
    print(f"\nFAILED: {e}")