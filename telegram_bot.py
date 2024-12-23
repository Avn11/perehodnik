import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import asyncio

# Укажите ваш токен бота
BOT_TOKEN = "7945799403:AAGcc9M7l5J44V8FIcicudeUQXyqJFh87Ss"

# Публичный username канала для проверки подписки
CHECK_CHANNEL = "@Nuqor"  # Убедитесь, что это правильный username канала
TARGET_CHANNEL = "https://t.me/Films_Film_Films"  # Канал, на который будет ссылаться бот после проверки подписки
RETRY_CHANNEL = "https://t.me/Nuqor"  # Канал, на который нужно подписаться, если не подписан

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объекта бота
bot = Bot(token=BOT_TOKEN)

# Создание диспетчера
dp = Dispatcher(bot)

# Клавиатура с кнопкой проверки подписки
check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Подписался, спасибо!", callback_data="check_subscription")]
])

# Стартовое сообщение
@dp.message(CommandStart())
async def start_command(message: types.Message):
    """Обрабатывает команду /start"""
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет👋 {user_name}, чтобы получить доступ к фильмам, подпишись на канал: {CHECK_CHANNEL}\n\n"
        "После подписки нажми на кнопку ниже, чтобы подтвердить, что ты подписался. ☺️",
        reply_markup=check_keyboard
    )

# Проверка подписки
@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    """Проверяет подписку пользователя"""
    user_id = callback_query.from_user.id
    try:
        # Проверка подписки
        member = await bot.get_chat_member(chat_id=CHECK_CHANNEL, user_id=user_id)

        if member.status in ["member", "administrator", "creator"]:
            # Если пользователь подписан
            await callback_query.message.answer(
                f"🎉 Отлично! Вот ваша ссылка на канал с фильмами: {TARGET_CHANNEL}"
            )
        else:
            # Если пользователь не подписан
            await callback_query.message.answer(
                f"Вы не подписаны на канал {CHECK_CHANNEL}. Пожалуйста, подпишитесь и попробуйте снова: {RETRY_CHANNEL}",
                reply_markup=check_keyboard
            )
    except Exception as e:
        # Если произошла ошибка, например, канал не найден
        logging.error(f"Ошибка при проверке подписки: {str(e)}")
        await callback_query.message.answer(
            "Произошла ошибка при проверке подписки. Попробуйте позже."
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
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(on_start())