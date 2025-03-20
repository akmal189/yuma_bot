from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from data.products import products

def start_keyboard():
    buttons = [
        [KeyboardButton(text="🍔 Меню")],
        [KeyboardButton(text="🛒 Корзина")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def categories_keyboard():
    buttons = [InlineKeyboardButton(text=cat, callback_data=f"category:{cat}") for cat in products]
    buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])

def products_keyboard(category):
    buttons = []
    for product_name, item in products[category].items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{product_name} — {item['price']} сум",
                callback_data=f"product:{product_name}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def main_menu_keyboard():
    buttons = [
        InlineKeyboardButton(text="🍔 Меню", callback_data="show_categories"),
        InlineKeyboardButton(text="🛒 Корзина", callback_data="show_cart")
    ]
    return InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])

def cart_keyboard_with_delete(cart):
    buttons = []
    for idx, item in enumerate(cart):
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ {item['name']} — {item['price']}₽",
                callback_data=f"remove_item:{idx}"
            )
        ])
    # Оплата и назад
    buttons.append([InlineKeyboardButton(text="✅ Добавить комментарий", callback_data="add_comment")])
    buttons.append([InlineKeyboardButton(text="✅ Оплатить онлайн", callback_data="pay_online")])
    buttons.append([InlineKeyboardButton(text="💵 Оплата при получении", callback_data="pay_cash")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)