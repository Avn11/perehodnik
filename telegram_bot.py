import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import asyncio
from aiohttp import web

# Укажите ваш токен бота
BOT_TOKEN = "7945799403:AAGcc9M7l5J44V8FIcicudeUQXyqJFh87Ss"

# Ссылка на канал для проверки подписки (полная ссылка)
CHECK_CHANNEL = "https://t.me/Nuqor"  # Замените на актуальную ссылку канала
TARGET_CHANNEL = "https://t.me/Films_Film_Films"  # Замените на нужный канал

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объекта бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатура с кнопкой проверки подписки
check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
])

# Стартовое сообщение
@dp.message(CommandStart())
async def start_command(message: types.Message):
    """Обрабатывает команду /start"""
    await message.answer(
        f"Привет {message.from_user.username}, чтобы получить доступ к фильмам подпишись на канал.\n\n"
        "После подписки нажмите на кнопку ниже, чтобы проверить.",
    )
    await message.answer(f"Вот ссылка на канал: {CHECK_CHANNEL}\nПожалуйста, подпишитесь!")
    await message.answer(
        "После подписки нажмите на кнопку ниже, чтобы проверить.",
        reply_markup=check_keyboard
    )

# Проверка подписки
@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member = await bot.get_chat_member(chat_id="@Nuqor", user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await callback_query.message.answer(
                f"🎉 Отлично! Вот ваша ссылка на целевой канал: {TARGET_CHANNEL}"
            )
        else:
            await callback_query.message.answer(
                f"Вы не подписаны на канал {CHECK_CHANNEL}.\nПожалуйста, подпишитесь и попробуйте снова.",
                reply_markup=check_keyboard
            )
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки для пользователя {user_id}: {str(e)}")
        await callback_query.message.answer("Вы не подписались. Попробуйте еще раз.")

# Удаление webhook
async def remove_webhook():
    await bot.delete_webhook()

# Настройка приложения aiohttp
async def on_start():
    logging.info("Removing webhook if exists...")
    await remove_webhook()

    webhook_url = "https://perehodnik-c7t4.onrender.com/webhook"
    logging.info(f"Устанавливаем Webhook по адресу: {webhook_url}")
    await bot.set_webhook(webhook_url)

    logging.info("Bot started!")

# Настройка aiohttp
async def handle_webhook(request):
    json_str = await request.json()
    update = types.Update(**json_str)
    await dp.process_update(update)
    return web.Response()

app = web.Application()
app.router.add_post('/webhook', handle_webhook)

# Запуск приложения
if __name__ == "__main__":
    # Обеспечиваем корректное ожидание on_start()
    asyncio.run(on_start())
    web.run_app(app, host="0.0.0.0", port=80)