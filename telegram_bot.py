import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher

# Замените на свои ключи
TELEGRAM_TOKEN = "7628342828:AAGpTOxvB6h5q5DKtsnpBybhH_ljV1Z794E"
TONCENTER_API_KEY = "96e65a2a16142db0361e74c72915a3c3611e04bc678c6b53eca3240d74a16c1a"
TELEGRAM_CHAT_ID = "7885730629"

# Эндпоинт TON Center API для получения информации о токене
TONCENTER_API_URL = "https://toncenter.com/api/v2/getTokenInfo"

# Создаем бота и диспетчер
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

def get_token_data(contract_address):
    """
    Функция для получения информации о токене по адресу контракта через TON Center API.
    """
    params = {
        "address": contract_address,
        "api_key": TONCENTER_API_KEY
    }
    try:
        response = requests.get(TONCENTER_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Ошибка получения данных по токену {contract_address}: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Исключение при получении данных для {contract_address}: {e}")
        return None

async def get_new_tokens():
    """
    Функция перебирает список новых токенов, получает их данные и возвращает список сообщений для отправки.
    """
    # Для примера используем статический список адресов новых токенов
    new_token_addresses = [
        "EQC5PXgKwNIcLtffu1OwWfo7dxW_1jbLjRfCKNk_7QKedsMZ",
        "EQAPki8c1ZR9jUodpQg_I5-PrITe_iHctzMYTSBS8lN0zOYV",
        "EQBvjexhDfOFNb28PVX36jOJLIrb9tn730cHqX076rLTp9BQ",
        "EQAS-THqoeKRzY2j78Cia7NPqHPop7xEoMDsGuAL__W3zHBz"
    ]
    alerts = []
    for address in new_token_addresses:
        token = get_token_data(address)
        if token:
            try:
                # Предполагаем, что данные содержат следующие ключи:
                liquidity = float(token.get("liquidity", 0))
                holders = int(token.get("holders", 0))
                volume = float(token.get("volume", 0))
                name = token.get("name", "Unknown")
                symbol = token.get("symbol", "N/A")
                
                # Фильтр: минимальная ликвидность 10 000 TON и более 50 холдеров
                if liquidity > 10000 and holders > 50:
                    alert_message = (
                        f"🔥 Новый токен найден: {name} ({symbol})\n"
                        f"📌 Контракт: {address}\n"
                        f"💰 Ликвидность: {liquidity} TON\n"
                        f"👥 Холдеры: {holders}\n"
                        f"📊 Объем: {volume} TON"
                    )
                    alerts.append(alert_message)
            except Exception as e:
                logging.error(f"Ошибка обработки токена {address}: {e}")
    return alerts

async def send_alerts():
    """
    Функция периодически (раз в минуту) проверяет новые токены и отправляет сигналы в Telegram.
    """
    while True:
        alerts = await get_new_tokens()
        for alert in alerts:
            await bot.send_message(TELEGRAM_CHAT_ID, alert)
        await asyncio.sleep(60)  # Проверять раз в минуту

async def main():
    # Запускаем фоновую задачу для отправки уведомлений
    asyncio.create_task(send_alerts())
    await dp.start_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())