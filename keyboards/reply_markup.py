from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton


def generate_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Оформить заказ")],
        [
            KeyboardButton(text="Корзина"),
            KeyboardButton(text="История заказов")
        ]
    ], resize_keyboard=True)
