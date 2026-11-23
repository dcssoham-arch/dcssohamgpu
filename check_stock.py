import os
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup

# Load credentials and trigger info from GitHub
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
GITHUB_EVENT = os.environ.get("GITHUB_EVENT_NAME")
GITHUB_SCHEDULE = os.environ.get("GITHUB_SCHEDULE")

WEEKLY_CRON = "30 3 * * 1"  # Mondays at 9:00 AM IST (03:30 UTC)
SMTP_HOST = ".".join(["smtp", "gmail", "com"])

URL = "https://onlinestpl.co.in"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def send_email(subject, body):
  if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
    raise ValueError(
        "Missing one or more GitHub Secrets: EMAIL_SENDER, EMAIL_PASSWORD, or"
        " EMAIL_RECEIVER"
    )

  msg = EmailMessage()
  msg.set_content(body)
  msg["Subject"] = subject
  msg["From"] = EMAIL_SENDER
  msg["To"] = EMAIL_RECEIVER

  with smtplib.SMTP_SSL(SMTP_HOST, 465) as smtp:
    smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
    smtp.send_message(msg)
  print(f"Email sent: {subject}")


def check_stock():
  try:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    page_text = soup.get_text().lower()
    add_to_cart_btn = soup.find("button", {"name": "add-to-cart"})

    is_in_stock = bool(add_to_cart_btn) or (
        "add to cart" in page_text and "out of stock" not in page_text
    )

    if is_in_stock:
      print("IN STOCK! Sending alert email...")
      send_email(
          subject="🚨 RTX 5070 FE IN STOCK ON STPL!",
          body=(
              "The NVIDIA GeForce RTX 5070 FE is IN STOCK at STPL!\n\n"
              f"Buy now: {URL}"
          ),
      )
    else:
      print("Status: Out of stock.")
      if GITHUB_EVENT == "workflow_dispatch":
        send_email(
            subject="✅ STPL RTX 5070 Bot Started",
            body=(
                "Your stock monitor is active and checking STPL every 5 "
                "minutes.\n\n"
                f"Monitored URL: {URL}\n"
                "Current status: Out of stock. You will receive an alert the "
                "moment it restocks."
            ),
        )
      elif GITHUB_SCHEDULE == WEEKLY_CRON:
        send_email(
            subject="📊 Weekly Report: STPL RTX 5070 Bot Still Running",
            body=(
                "Weekly health check: Your stock monitor is still active and "
                "scanning STPL every 5 minutes.\n\n"
                f"Monitored URL: {URL}\n"
                "Current status: Still out of stock."
            ),
        )

  except Exception as e:
    print(f"Error checking stock: {e}")


if __name__ == "__main__":
  check_stock()
