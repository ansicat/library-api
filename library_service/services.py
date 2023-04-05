import os

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def borrowing_send_notification(message):
    try:
        requests.post(
            TELEGRAM_URL, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}
        )
    except Exception as e:
        print("ERROR: ", e)
