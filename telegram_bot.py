import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types

# Твой Telegram-токен
TOKEN = "7860834182:AAH-12wehh4eYfJyr6uVXQp9xa19g5cKq8c"

# API-ключи (если нужны)
DEXTON_API_URL = "https://api.dexton.io/v1/tokens"
HEADERS = {"Authorization": "ТВОЙ_API_КЛЮЧ"}

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Функция для получения новых токенов
async def get_new_tokens():
    try:
        response = requests.get(DEXTON_API_URL, headers=HEADERS)
        data = response.json()

        new_tokens = []
        for token in data:
            if token["liquidity"] > 10000 and token["holders"] > 50:
                new_tokens.append(
                    f"🔥 Новый токен найден: {token['name']} ({token['symbol']})\n"
                    f"📌 Контракт: {token['contract_address']}\n"
                    f"💰 Ликвидность: {token['liquidity']} TON\n"
                    f"👥 Холдеры: {token['holders']}\n"
                    f"📊 Объем: {token['volume']} TON"
                )

        return new_tokens
    except Exception as e:
        logging.error(f"Ошибка получения токенов: {e}")
        return []

# Функция для отправки сообщений
async def send_alerts():
    while True:
        new_tokens = await get_new_tokens()
        for token in new_tokens:
            await bot.send_message("ТВОЙ_CHAT_ID", token)
        await asyncio.sleep(60)  # Проверка раз в минуту

# Запуск бота
async def main():
    asyncio.create_task(send_alerts())
    await dp.start_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())