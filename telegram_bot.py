import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio
from aiohttp import web

# Укажите ваш токен бота
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"

# Ссылка на канал для проверки подписки
CHECK_CHANNEL_USERNAME = "Nuqor"  # Укажите username канала без "@"
TARGET_CHANNEL_LINK = "https://t.me/Films_Film_Films"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объекта бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатура с кнопкой проверки подписки
check_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
    ]
)

# Стартовое сообщение
@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обрабатывает команду /start"""
    await message.answer(
        f"Привет, {message.from_user.username}!\n"
        f"Чтобы получить доступ к фильмам, подпишитесь на канал {CHECK_CHANNEL_USERNAME}.\n"
        "После подписки нажмите на кнопку ниже, чтобы проверить.",
        reply_markup=check_keyboard
    )

# Проверка подписки
@dp.callback_query_handler(lambda callback_query: callback_query.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        # Проверяем подписку пользователя
        member = await bot.get_chat_member(chat_id=f"@{CHECK_CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await callback_query.message.answer(
                f"🎉 Отлично! Вот ваша ссылка на канал с фильмами: {TARGET_CHANNEL_LINK}"
            )
        else:
            await callback_query.message.answer(
                f"Вы не подписаны на канал @{CHECK_CHANNEL_USERNAME}.\nПожалуйста, подпишитесь и попробуйте снова.",
                reply_markup=check_keyboard
            )
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки для пользователя {user_id}: {e}")
        await callback_query.message.answer(
            f"Не удалось проверить подписку. Убедитесь, что вы подписаны на @{CHECK_CHANNEL_USERNAME}."
        )

# Удаление вебхука
async def remove_webhook():
    await bot.delete_webhook()

# Настройка приложения aiohttp
async def on_startup(app):
    logging.info("Удаляем старый вебхук (если есть)...")
    await remove_webhook()

    webhook_url = "https://perehodnik-c7t4.onrender.com/webhook"
    logging.info(f"Устанавливаем вебхук по адресу: {webhook_url}")
    await bot.set_webhook(webhook_url)

    logging.info("Бот запущен!")

async def on_shutdown(app):
    logging.info("Останавливаем бота...")
    await remove_webhook()
    await bot.session.close()

# Обработчик вебхука
async def handle_webhook(request):
    try:
        json_str = await request.json()
        update = types.Update(**json_str)
        await dp.process_update(update)
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука: {e}")
    return web.Response()

# Создание веб-приложения
app = web.Application()
app.router.add_post('/webhook', handle_webhook)

# Регистрация событий старта и остановки
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# Запуск приложения
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=80)