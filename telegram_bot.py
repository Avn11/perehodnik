import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Укажите ваш токен бота
BOT_TOKEN = "7945799403:AAGcc9M7l5J44V8FIcicudeUQXyqJFh87Ss"
WEBHOOK_PATH = "/webhook"  # Путь Webhook
WEBAPP_HOST = "0.0.0.0"  # Хост для сервера
WEBAPP_PORT = int(os.getenv("PORT", 3000))  # Порт для сервера

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Ссылка на канал для проверки подписки
CHECK_CHANNEL = "https://t.me/Nuqor"
TARGET_CHANNEL = "https://t.me/Films_Film_Films"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатура с кнопкой проверки подписки
check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
])

@dp.message(CommandStart())
async def start_command(message: types.Message):
    """Отправляет стартовое сообщение"""
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! Чтобы получить доступ к фильмам, подпишись на канал:\n\n"
        f"{CHECK_CHANNEL}\n\n"
        "После подписки нажми на кнопку ниже, чтобы проверить.",
        reply_markup=check_keyboard
    )

@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    """Проверяет подписку пользователя"""
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
        await callback_query.message.answer("Произошла ошибка. Попробуйте позже.")

async def on_startup(app):
    """Устанавливает Webhook на старте"""
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOST')}{WEBHOOK_PATH}"
    logging.info(f"Устанавливаем Webhook по адресу: {webhook_url}")
    await bot.set_webhook(url=webhook_url)

async def on_shutdown(app):
    """Удаляет Webhook при остановке"""
    await bot.delete_webhook()

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

if __name__ == "__main__":
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)