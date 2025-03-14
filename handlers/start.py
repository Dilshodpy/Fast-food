from config import bot, dp
from aiogram.types import Message
from database import DatabaseTools
from keyboards.reply_markup import generate_main_menu


@dp.message_handler(commands=["start"])
async def start(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    await bot.send_message(chat_id, f"Привет, {full_name} !")
    await register_user(message)
    await register_cart(message)
    await show_main_menu(message)


async def register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name

    tools = DatabaseTools()
    tools.register_user(
        full_name=full_name,
        chat_id=chat_id
    )


async def register_cart(message: Message):
    chat_id = message.chat.id

    user_id = DatabaseTools().get_user_id(chat_id)
    cart = DatabaseTools().get_cart(user_id)
    if not cart:
        DatabaseTools().register_cart(
            user_id=user_id
        )


async def show_main_menu(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Выберите направление: ", reply_markup=generate_main_menu())
