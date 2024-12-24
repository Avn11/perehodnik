import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
import asyncio

# Укажите ваш токен бота
BOT_TOKEN = "7945799403:AAGcc9M7l5J44V8FIcicudeUQXyqJFh87Ss"

# Ссылка на канал для проверки подписки (полная ссылка)
CHECK_CHANNEL = "https://t.me/Nuqor"  # Замените на актуальную ссылку канала
TARGET_CHANNEL = "https://t.me/YourTargetChannel"  # Замените на нужный канал

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
    # Сначала отправляется ссылка на канал
    await message.answer(
        f"Привет! Чтобы получить доступ к интересному контенту, подпишитесь на наш канал: {CHECK_CHANNEL}.\n\n"
        "После подписки нажмите на кнопку ниже, чтобы проверить.",
    )
    # Отправка ссылки на канал
    await message.answer(f"Вот ссылка на канал: {CHECK_CHANNEL}\nПожалуйста, подпишитесь!")

    # И добавляем кнопку для проверки подписки
    await message.answer(
        "После подписки нажмите на кнопку ниже, чтобы проверить.",
        reply_markup=check_keyboard
    )

# Проверка подписки
@dp.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback_query: types.CallbackQuery):
    """Проверяет подписку пользователя по юзернейму канала"""
    user_id = callback_query.from_user.id
    try:
        # Проверка подписки по юзернейму канала (первый параметр - это @канал)
        member = await bot.get_chat_member(chat_id="@Nuqor", user_id=user_id)

        if member.status in ["member", "administrator", "creator"]:
            # Если пользователь подписан
            await callback_query.message.answer(
                f"🎉 Отлично! Вот ваша ссылка на целевой канал: {TARGET_CHANNEL}"
            )
        else:
            # Если пользователь не подписан
            await callback_query.message.answer(
                f"Вы не подписаны на канал {CHECK_CHANNEL}.\nПожалуйста, подпишитесь и попробуйте снова.",
                reply_markup=check_keyboard
            )
    except Exception as e:
        # Логирование ошибки
        logging.error(f"Ошибка при проверке подписки для пользователя {user_id}: {str(e)}")
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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(on_start())