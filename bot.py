import os
import json
import requests
from datetime import datetime
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://api.exchangerate.host/latest?base=USD&symbols=KZT"
DATA_FILE = "storage/data.json"

bot = Bot(token=TELEGRAM_TOKEN)


def get_current_rate():
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("result") == "success":
            return round(data["rates"]["KZT"], 2)
        else:
            print("Ошибка API:", data)
            return None
    except Exception as e:
        print("Ошибка при получении курса:", e)
        return None


#def load_previous_rate():
#    if not os.path.exists(DATA_FILE):
 #       return None
  #  try:
   #     with open(DATA_FILE, "r") as f:
    #        data = json.load(f)
     #       return data.get("rate")
    #except Exception:
     #   return None


def load_previous_rate():
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                return data[-1].get("rate")
    except Exception:
        return None



#def save_rate(rate):
 #   os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
  #  with open(DATA_FILE, "w") as f:
   #     json.dump({"rate": rate, "timestamp": datetime.now().isoformat()}, f)



def save_rate(rate):
    data = []

    # Если файл уже есть, загружаем старые данные
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = []

    # Добавляем новую запись
    data.append({
        "rate": rate,
        "timestamp": datetime.now().isoformat()
    })

    # Сохраняем обратно
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)




def send_message(text):
    bot.send_message(chat_id=CHAT_ID, text=text)


def main():
    current_rate = get_current_rate()
    if current_rate is None:
        return

    previous_rate = load_previous_rate()

    message = f"💰 Курс USD → KZT: {current_rate} ₸"

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
