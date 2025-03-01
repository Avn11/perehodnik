import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = "7211119418:AAEyibsFiC_W-UClM-zyjbIhtYUrvwpxcz8"
CHAT_ID = "7211119418"  # ID чата, куда бот будет слать токены
API_URL = "https://api.geckoterminal.com/api/v2/networks/ton/tokens"
MIN_HOLDERS = 50     
MIN_LIQUIDITY = 1000  
MIN_VOLUME = 500  
CHECK_INTERVAL = 300  # Интервал проверки (в секундах) = 5 минут
TOP_TOKENS = []

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
found_tokens = set()  # Хранит уже отправленные токены

# === ОБУЧЕНИЕ МОДЕЛИ ===
def train_model():
    global model
    X_train = np.array([
        [100, 5000, 1000],  
        [30, 800, 300],  
        [200, 10000, 5000],  
        [10, 100, 50]  
    ])
    y_train = np.array([1, 0, 1, 0])  
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    logging.info("🎯 Модель обучена")

# === ФУНКЦИЯ ДЛЯ ПОИСКА ТОКЕНОВ ===
async def find_new_tokens():
    global found_tokens
    while True:
        try:
            response = requests.get(API_URL)
            data = response.json()
            tokens = data.get("data", [])
            
            good_tokens = []
            for token in tokens:
                try:
                    address = token["id"]
                    holders = int(token["attributes"]["holders"])
                    liquidity = float(token["attributes"]["liquidity"])
                    volume = float(token["attributes"]["volume_24h"])

                    prediction = model.predict([[holders, liquidity, volume]])[0]

                    if prediction == 1 and address not in found_tokens:  
                        found_tokens.add(address)
                        good_tokens.append(f"{address}\n📌 Холдеры: {holders} | 💰 Ликвидность: {liquidity}$ | 📊 Объем: {volume}$")
                except Exception as e:
                    logging.warning(f"⚠ Ошибка при обработке токена: {e}")

            if good_tokens:
                await bot.send_message(CHAT_ID, "\n\n".join(good_tokens))
            
        except Exception as e:
            logging.error(f"Ошибка при получении данных: {e}")

        await asyncio.sleep(CHECK_INTERVAL)  

# === КОМАНДА /start ===
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("🚀 Я ищу новые мемкоины в TON 24/7. Жди уведомлений!")

# === ГЛАВНАЯ ФУНКЦИЯ ===
async def main():
    train_model()
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(find_new_tokens())  # Запускаем цикл поиска токенов
    await dp.start_polling(bot)

# === ЗАПУСК БОТА ===
if __name__ == "__main__":
    asyncio.run(main())