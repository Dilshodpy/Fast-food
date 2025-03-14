from config import bot, dp
from aiogram.types import CallbackQuery, Message
from database import DatabaseTools
from datetime import datetime

from pprint import pprint


@dp.callback_query_handler(lambda call: call.data.startswith("create-order"))
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, cart_id = call.data.split("_")
    cart_id = int(cart_id)

    user_id = DatabaseTools().get_user_id(chat_id)
    _, total_price, total_quantity = DatabaseTools().get_cart(user_id)
    now_datetime = str(datetime.now().strftime("%Y-%m-%d %H:%M"))

    DatabaseTools().create_order(
        cart_id,
        user_id,
        now_datetime,
        total_price,
        total_quantity
    )

    DatabaseTools().cart_in_order(cart_id)
    await bot.answer_callback_query(call.id, "Заказ успешно добавлен !")


@dp.message_handler(lambda message: message.text.startswith("История заказов"))
async def show_list_orders(message: Message):
    chat_id = message.chat.id

    user_id = DatabaseTools().get_user_id(chat_id)
    orders = DatabaseTools().get_orders(user_id)

    if not orders:
        await bot.send_message(chat_id, "Список заказов пуст !")
        return

    pprint(orders)
    # TODO:
    order_id, product_index = 0, 0
    send_message_flag = False
    for order in orders:
        order_text_status = ""
        if order_id != order[0]:
            try:
                await bot.send_message(chat_id, order_text_status)
            except:
                pass
            order_id = order[0]
            order_text_status += f"Заказ № {order_id}\n\n"
        order_text_status += f"\n    {product_index}. {order[1]}\n" \
                             f"        Количество: {order[2]} шт.\n" \
                             f"        Стоимость: {order[3]} сум.\n"

    order_text = "Список ваших заказов:"
    order_index, product_index = 0, 0
    order_id = 0
    for order in orders:
        if order_id != order[0]:
            order_index += 1
            order_id = order[0]
            product_index = 0
            order_text += f"\n\nЗаказ № {order_index}/ Дата создания: {order[4]}"
        product_index += 1
        order_text += f"\n    {product_index}. {order[1]}\n" \
                      f"        Количество: {order[2]} шт.\n" \
                      f"        Стоимость: {order[3]} сум.\n"

        # if :
        #     order_text += f"\nОбщая кол-во товаров в заказе: {order[6]}\n" \
        #                   f"Общая стоимость заказа: {order[5]}"

    await bot.send_message(chat_id, order_text)
