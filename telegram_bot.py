import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import asyncio

# Укажите ваш токен бота
BOT_TOKEN = "7945799403:AAGcc9M7l5J44V8FIcicudeUQXyqJFh87Ss"

# ID канала для проверки подписки
CHECK_CHANNEL = "@Nuqor"
TARGET_CHANNEL = "https://t.me/Films_Film_Films"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объекта бота
bot = Bot(token=BOT_TOKEN)

# Создание объекта Dispatcher
dp = Dispatcher()

# Клавиатура с кнопкой проверки подписки
check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
])

# Стартовое сообщение
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """Обрабатывает команду /start"""
    await message.answer(
        f"Привет! Чтобы получить доступ к интересному контенту, подпишитесь на наш канал: {CHECK_CHANNEL}.\n\n"
        "После подписки нажмите на кнопку ниже, чтобы проверить.",
        reply_markup=check_keyboard
    )

# Проверка подписки
@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    """Проверяет подписку пользователя"""
    user_id = callback_query.from_user.id
    member = await bot.get_chat_member(chat_id=CHECK_CHANNEL, user_id=user_id)

    if member.status in ["member", "administrator", "creator"]:
        # Если пользователь подписан
        await callback_query.message.answer(
            f"🎉 Отлично! Вот ваша ссылка: {TARGET_CHANNEL}"
        )
    else:
        # Если пользователь не подписан
        await callback_query.message.answer(
            f"Вы не подписаны на канал {CHECK_CHANNEL}.\nПожалуйста, подпишитесь и попробуйте снова.",
            reply_markup=check_keyboard
        )

# Удаление webhook
async def remove_webhook():
    """Удалить webhook, если он был установлен"""
    await bot.delete_webhook()

# Запуск бота
async def on_start():
    logging.info("Removing webhook if exists...")
    await remove_webhook()
    logging.info("Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(on_start())