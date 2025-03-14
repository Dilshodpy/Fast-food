from aiogram import Bot, Dispatcher

import os
from dotenv import load_dotenv

load_dotenv()


# Режим разработки
DEBUG = True

token = os.getenv("BOT_TOKEN")
bot = Bot(token)
dp = Dispatcher(bot)
