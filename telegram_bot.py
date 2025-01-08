from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ParseMode
import re

API_TOKEN = '7860834182:AAH-12wehh4eYfJyr6uVXQp9xa19g5cKq8c'
SOURCE_CHAT_ID = -100123456789  # ID группы-источника
TARGET_CHAT_ID = -100987654321  # ID группы, куда пересылаются сообщения
OLD_BOT_USERNAME = '@OLD_BOT'   # Имя старого бота
NEW_BOT_USERNAME = '@XBOTROBOT' # Имя нового бота

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(chat_id=SOURCE_CHAT_ID)
async def forward_and_replace(message: types.Message):
    # Заменяем старого бота на нового
    new_text = re.sub(re.escape(OLD_BOT_USERNAME), NEW_BOT_USERNAME, message.text)
    
    # Добавляем плашку
    new_text += "\n\nПокупка через @XBOTROBOT"

    # Отправляем сообщение в целевую группу
    await bot.send_message(chat_id=TARGET_CHAT_ID, text=new_text, parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)