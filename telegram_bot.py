import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = "7211119418:AAEyibsFiC_W-UClM-zyjbIhtYUrvwpxcz8"  # Твой токен бота
CHAT_ID = "-4623096704"  # Твой ID или ID чата (проверь, что правильно)
API_URL = "https://api.geckoterminal.com/api/v2/networks/ton/tokens"
MIN_HOLDERS = 50      # Минимальное число держателей
MIN_LIQUIDITY = 1000  # Минимальная ликвидность
MIN_VOLUME = 500      # Минимальный объем торгов
CHECK_INTERVAL = 300  # Проверка каждые 5 минут

# Настройка логирования (чтобы видеть, что происходит)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
found_tokens = set()  # Список уже найденных токенов, чтобы не повторяться

# === ОБУЧЕНИЕ МОДЕЛИ ===
def train_model():
    global model
    # Пример данных для обучения (в будущем добавь больше данных)
    X_train = np.array([
        [100, 5000, 1000],  # Хороший токен
        [30, 800, 300],     # Плохой токен
        [200, 10000, 5000], # Хороший токен
        [10, 100, 50]       # Плохой токен
    ])
    y_train = np.array([1, 0, 1, 0])  # 1 = хороший, 0 = плохой
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    logging.info("🎯 Модель обучена")

# === ПОИСК НОВЫХ ТОКЕНОВ ===
async def find_new_tokens():
    global found_tokens
    while True:
        try:
            # Получаем данные с API
            response = requests.get(API_URL)
            data = response.json()
            tokens = data.get("data", [])
            
            good_tokens = []  # Список перспективных токенов
            for token in tokens:
                try:
                    address = token["id"]
                    holders = int(token["attributes"]["holders"])
                    liquidity = float(token["attributes"]["liquidity"])
                    volume = float(token["attributes"]["volume_24h"])

                    # Проверяем минимальные значения
                    if holders >= MIN_HOLDERS and liquidity >= MIN_LIQUIDITY and volume >= MIN_VOLUME:
                        # Проверяем через модель
                        prediction = model.predict([[holders, liquidity, volume]])[0]
                        if prediction == 1 and address not in found_tokens:
                            found_tokens.add(address)
                            good_tokens.append(f"{address}\n📌 Холдеры: {holders} | 💰 Ликвидность: {liquidity}$ | 📊 Объем: {volume}$")
                except Exception as e:
                    logging.warning(f"⚠ Ошибка при обработке токена: {e}")

            # Отправляем сообщения, разбивая на части по 10 токенов
            if good_tokens:
                for i in range(0, len(good_tokens), 10):
                    chunk = good_tokens[i:i+10]
                    try:
                        await bot.send_message(CHAT_ID, "\n\n".join(chunk))
                        logging.info("✅ Сообщение отправлено")
                    except Exception as e:
                        logging.error(f"❌ Ошибка при отправке: {e}")
            
        except Exception as e:
            logging.error(f"❌ Ошибка при получении данных: {e}")

        await asyncio.sleep(CHECK_INTERVAL)  # Ждем 5 минут

# === КОМАНДА /start ===
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("🚀 Я ищу новые мемкоины в TON 24/7. Жди уведомлений!")

# === ГЛАВНАЯ ФУНКЦИЯ ===
async def main():
    train_model()  # Обучаем модель
    await bot.delete_webhook(drop_pending_updates=True)  # Удаляем старые вебхуки
    asyncio.create_task(find_new_tokens())  # Запускаем поиск токенов
    await dp.start_polling(bot)  # Запускаем бота

# === ЗАПУСК БОТА ===
if __name__ == "__main__":
    asyncio.run(main())
​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​