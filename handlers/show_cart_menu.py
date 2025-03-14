from config import bot, dp
from aiogram.types import Message, CallbackQuery
from database import DatabaseTools
from keyboards.inline_markup import generate_cart_menu


@dp.message_handler(lambda message: message.text.startswith("Корзина"))
async def show_cart_menu(message: Message, edit: bool = False):
    chat_id = message.chat.id
    message_id = message.message_id
    user_id = DatabaseTools().get_user_id(chat_id)
    cart_id = DatabaseTools().get_cart_id(user_id)
    cart_products = DatabaseTools().get_cart_products(cart_id)
    if not cart_products:
        await bot.send_message(chat_id, "Корзина пуста !")
        return

    cart_text = f"Список товаров в корзине:\n\n"
    products_info = []

    i = 0
    for cart_product_id, product_name, quantity, final_price in cart_products:
        i += 1
        products_info.append((cart_product_id, f"❌  {product_name}"))
        cart_text += f"{i}. <b>{product_name}</b>\n" \
                     f"    <i>Кол-во в корзине:</i> {quantity}\n" \
                     f"    <i>Общая стоимость:</i> {final_price} сум.\n\n"

    total_price, total_quantity = DatabaseTools().get_info_cart(cart_id)
    cart_text += f"Общее кол-во продуктов в корзине: {total_quantity}\n" \
                 f"Общая стоимость корзины: {total_price} сум."

    if not edit:
        await bot.send_message(chat_id, cart_text, parse_mode="HTML",
                               reply_markup=generate_cart_menu(products_info, cart_id))
    else:
        await bot.edit_message_text(cart_text, chat_id, message_id, parse_mode="HTML",
                                    reply_markup=generate_cart_menu(products_info, cart_id))


@dp.callback_query_handler(lambda call: call.data.startswith("add-cart"))
async def add_cart_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_id, qty = call.data.split("_")
    product_id, qty = int(product_id), int(qty)

    product_name, product_price = DatabaseTools().get_product(product_id)[:2]
    final_price = product_price * qty
    user_id = DatabaseTools().get_user_id(chat_id)
    cart_id = DatabaseTools().get_cart_id(user_id)

    edit_status = DatabaseTools().create_cart_product(
        cart_id,
        product_name,
        product_id,
        qty,
        final_price
    )

    if edit_status:
        await bot.answer_callback_query(call.id, "Количесво продукта успешно обновлено !")
    else:
        await bot.answer_callback_query(call.id, "Продукт успешно добавлен !")

    DatabaseTools().recalc_cart(cart_id)


@dp.callback_query_handler(lambda call: call.data.startswith("delete-cart"))
async def delete_cart_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, cart_product_id = call.data.split("_")
    cart_product_id = int(cart_product_id)

    DatabaseTools().delete_cart_product(cart_product_id)

    user_id = DatabaseTools().get_user_id(chat_id)
    cart_id = DatabaseTools().get_cart_id(user_id)
    DatabaseTools().recalc_cart(cart_id)

    await show_cart_menu(
        message=call.message,
        edit=True
    )
