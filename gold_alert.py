import requests
import json
import time
import os

from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://api.chnwt.dev/thai-gold-api/latest"
STATE_FILE = "state.json"
CONFIG_FILE = "config.json"


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })


def get_gold_price():
    r = requests.get(API_URL, timeout=10)
    data:str = r.json()
    price_sell_str = data["response"]["price"]["gold"]["sell"].replace(",","")
    price_sell_num = float(price_sell_str)
    # ราคาทองคำแท่งขายออก
    return price_sell_num


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    config = load_json(CONFIG_FILE)
    state = load_json(STATE_FILE)

    now = time.time()
    price = get_gold_price()

    last_price = state["last_price"]
    last_alert = state["last_alert_time"]

    cooldown = config["cooldown_minutes"] * 60

    alert_messages = []

    # price alert when current > last_price 
    diff = abs(price - last_price)
    if diff >= config["notify_change_baht"]:
        alert_messages.append(f"ราคาขยับ {diff} บาท\nตอนนี้: {price}")

    # cooldown
    if alert_messages and now - last_alert > cooldown:
        msg = "\n\n".join(alert_messages)
        send_telegram(msg)

        state["last_alert_time"] = now

    state["last_price"] = price
    save_json(STATE_FILE, state)


if __name__ == "__main__":
    main()
