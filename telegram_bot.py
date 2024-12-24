import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import asyncio

# Укажите ваш токен бота
BOT_TOKEN = "7945799403:AAGcc9M7l5J44V8FIcicudeUQXyqJFh87Ss"  # Замените на ваш токен
CHECK_CHANNEL = "https://t.me/Nuqor"  # Ссылка на канал
TARGET_CHANNEL = "https://t.me/Films_Film_Films"  # Ссылка на целевой канал

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объекта бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатура с кнопкой проверки подписки
check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Я подписался! ✅", callback_data="check_subscription")]
])

# Обработка команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    """Обрабатывает команду /start"""
    user_name = message.from_user.username or message.from_user.full_name or "друг"
    
    # Приветствие и ссылка на канал
    await message.answer(
        f"Привет, {user_name}! 👋 Чтобы получить доступ к Конану с фильмами, подпишись на этот канал:\n{CHECK_CHANNEL}"
    )
    
    # Отправка кнопки для проверки подписки
    await message.answer(
        "После подписки нажми на кнопку! 👇",
        reply_markup=check_keyboard
    )

# Проверка подписки
@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    """Проверяет подписку пользователя"""
    user_id = callback_query.from_user.id
    
    # Проверка подписки
    member = await bot.get_chat_member(chat_id="@Nuqor", user_id=user_id)  # chat_id в формате @юзернейм канала
    if member.status in ["member", "administrator", "creator"]:
        # Пользователь подписан
        await callback_query.message.answer(
            f"Спасибо 🙏, вот твоя ссылка! 🎉\n{TARGET_CHANNEL}\nПриятного просмотра! ☺️"
        )
    else:
        # Пользователь не подписан
        await callback_query.message.answer(
            f"Вы не подписаны на канал {CHECK_CHANNEL}.\n"
            "Пожалуйста, подпишитесь и попробуйте снова.",
            reply_markup=check_keyboard
        )

# Удаление webhook
async def remove_webhook():
    """Удаляет webhook, если он установлен"""
    await bot.delete_webhook()

# Запуск бота
async def on_start():
    logging.info("Removing webhook if exists...")
    await remove_webhook()
    logging.info("Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(on_start())