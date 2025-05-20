import os
import json
import requests
from datetime import datetime
from telegram import Bot

# Получаем токены из переменных окружения (GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.environ["CHAT_ID"]


API_KEY = os.getenv("API_KEY")  # сохрани ключ в секретах GitHub и передавай в переменных окружения
API_URL = f"https://api.exchangerate.host/latest?base=USD&symbols=KZT&access_key={API_KEY}"
DATA_FILE = "storage/data.json"


bot = Bot(token=TELEGRAM_TOKEN)


def get_current_rate():
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        if not data.get("success", False):
            print("Ошибка API:", data.get("error", {}))
            return None
        rate = data["rates"]["KZT"]
        return round(rate, 2)
    except Exception as e:
        print("Ошибка при получении курса:", e)
        return None


def load_previous_rate():
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return data.get("rate")
    except Exception:
        return None


def save_rate(rate):
    with open(DATA_FILE, "w") as f:
        json.dump({"rate": rate, "timestamp": datetime.now().isoformat()}, f)


def send_message(text):
    bot.send_message(chat_id=CHAT_ID, text=text)


def main():
    current_rate = get_current_rate()
    if current_rate is None:
        return

    previous_rate = load_previous_rate()

    message = f"💰 Курс USD: {current_rate} ₽"

    if previous_rate is not None:
        if current_rate > previous_rate:
            message += "\n📈 Курс вырос 📈"
        elif current_rate < previous_rate:
            message += "\n📉 Курс упал 📉"
        else:
            message += "\n➖ Без изменений"

    send_message(message)
    save_rate(current_rate)


if __name__ == "__main__":
    main()
