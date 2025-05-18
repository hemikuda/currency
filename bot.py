import os
import json
import requests
from dotenv import load_dotenv
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler

# Load .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CURRENCY = "USD"

DATA_FILE = "data.json"
API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

bot = Bot(token=TELEGRAM_TOKEN)
scheduler = BlockingScheduler()

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def fetch_usd_rate():
    response = requests.get(API_URL)
    data = response.json()
    return round(data["Valute"][CURRENCY]["Value"], 2)

def check_rate():
    data = load_data()
    current_rate = fetch_usd_rate()
    prev_rate = data.get(CURRENCY, {}).get("current", current_rate)

    message = None
    if current_rate > prev_rate:
        message = f"\u2B06 USD вырос: {prev_rate} ➜ {current_rate}"
    elif current_rate < prev_rate:
        message = f"\u2B07 USD упал: {prev_rate} ➜ {current_rate}"
    else:
        message = f"USD не изменился: {current_rate}"

    bot.send_message(chat_id=CHAT_ID, text=message)

    # Обновляем данные
    data[CURRENCY] = {"previous": prev_rate, "current": current_rate}
    save_data(data)

# Проверка каждый час
scheduler.add_job(check_rate, "interval", hours=1)

if __name__ == "__main__":
    print("Бот запущен...")
    check_rate()
    scheduler.start()
