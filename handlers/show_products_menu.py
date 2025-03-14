from config import bot, dp
from aiogram.types import Message, CallbackQuery
from database import DatabaseTools

from keyboards.inline_markup import (
    generate_categories_menu,
    generate_products_menu,
    generate_product_detail_menu
)


@dp.message_handler(lambda message: message.text.startswith("Оформить заказ"))
async def show_categories_menu(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Выберите категорию: ",
                           reply_markup=generate_categories_menu())


@dp.callback_query_handler(lambda call: call.data.startswith("category"))
async def show_products_menu(call: CallbackQuery):
    _, category_id = call.data.split("_")
    category_id = int(category_id)

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    await bot.edit_message_text(
        "Выберите продукт: ",
        chat_id,
        message_id,
        reply_markup=generate_products_menu(category_id)
    )


@dp.callback_query_handler(lambda call: call.data.startswith("product"))
async def show_detail_product_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_pk = call.data.split("_")
    product_pk = int(product_pk)

    title, price, preview, ingredients = DatabaseTools().get_product(product_pk)
    caption = f"Название продукта: {title}\n\nСтоимость: {price}\nСостав: {ingredients}"

    with open(preview, mode="rb") as photo:
        await bot.send_photo(
            chat_id,
            photo,
            caption,
            reply_markup=generate_product_detail_menu(product_pk, current_qty=0)
        )


@dp.callback_query_handler(lambda call: call.data.startswith("action"))
async def action_product_detail_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    _, action, product_pk, current_qty = call.data.split("_")
    product_pk, current_qty = int(product_pk), int(current_qty)

    if action == "minus" and current_qty > 0:
        current_qty -= 1
    elif action == "plus" and current_qty < 10:
        current_qty += 1
    elif action == str(current_qty):
        await bot.answer_callback_query(call.id, "Текущее выбранное кол-во")
        return
    else:
        await bot.answer_callback_query(call.id, "Данное кол-во выходит за допустимый диапазон")
        return

    await bot.edit_message_reply_markup(chat_id, message_id,
                                        reply_markup=generate_product_detail_menu(product_pk, current_qty))
