from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from database import DatabaseTools


def build_keyboard(markup: InlineKeyboardMarkup, lst: list, prefix: str, in_row: int = 2):
    rows = len(lst) // in_row
    if len(lst) % in_row != 0:
        rows += 1

    start = 0
    end = in_row

    for _ in range(rows):
        row = []
        for pk, title in lst[start:end]:
            row.append(
                InlineKeyboardButton(text=title, callback_data=f"{prefix}_{pk}")
            )
        markup.row(*row)
        start = end
        end += in_row


def generate_categories_menu():
    markup = InlineKeyboardMarkup()
    categories = DatabaseTools().get_categories()
    build_keyboard(
        markup=markup,
        lst=categories,
        prefix="category"
    )
    return markup


def generate_products_menu(category_id: int):
    markup = InlineKeyboardMarkup()
    products = DatabaseTools().get_products(category_id)
    build_keyboard(
        markup=markup,
        lst=products,
        prefix="product"
    )
    return markup


def generate_product_detail_menu(product_id: int, current_qty: int):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text="-", callback_data=f"action_minus_{product_id}_{current_qty}"),
        InlineKeyboardButton(text=str(current_qty), callback_data=f"action_{current_qty}_{product_id}_{current_qty}"),
        InlineKeyboardButton(text="+", callback_data=f"action_plus_{product_id}_{current_qty}")
    )
    markup.row(
        InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add-cart_{product_id}_{current_qty}")
    )
    return markup


def generate_cart_menu(products_info: list, cart_id: int):
    markup = InlineKeyboardMarkup()

    build_keyboard(
        markup=markup,
        lst=products_info,
        prefix="delete-cart",
    )

    markup.row(
        InlineKeyboardButton(text="🚀  Оформить заказ", callback_data=f"create-order_{cart_id}")
    )
    return markup
