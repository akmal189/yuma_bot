from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from data.products import products
from localization import get_message

def start_keyboard(lang):
    buttons = [
        [KeyboardButton(text=get_message("buttons.menu", lang))],
        [KeyboardButton(text=get_message("buttons.cart", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def categories_keyboard(lang):
    keyboard = InlineKeyboardMarkup()
    for category in products.keys():
        callback_data = f"category_{category}"
        print(f"✅ Создана кнопка: {category}, callback_data: {callback_data}")  # Лог кнопок
        keyboard.add(InlineKeyboardButton(text=category, callback_data=callback_data))
    return keyboard

def products_keyboard(category, products, lang):
    # buttons = []
    # for product_name, item in products[category].items():
    #     buttons.append([
    #         InlineKeyboardButton(
    #             text=f"{product_name} — {item['price']} сум",
    #             callback_data=f"product:{product_name}"
    #         )
    #     ])
    # buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")])
    # return InlineKeyboardMarkup(inline_keyboard=buttons)
    keyboard = [
        [KeyboardButton(text=product[1])] for product in products
    ]
    keyboard.append([KeyboardButton(text=get_message("buttons.back", lang))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def main_menu_keyboard(lang):
    # buttons = [
    #     InlineKeyboardButton(text="🍔 Меню", callback_data="show_categories"),
    #     InlineKeyboardButton(text="🛒 Корзина", callback_data="show_cart")
    # ]
    # return InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_message("buttons.menu", lang)),
                KeyboardButton(text=get_message("buttons.cart", lang))
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

def cart_keyboard_with_delete(cart: dict, lang: str):
    keyboard = []

    # Добавляем кнопки для удаления каждого товара
    for product_name, details in cart.items():
        price = details["price"]
        keyboard.append([InlineKeyboardButton(text=f"❌ {product_name} — {price} сум", callback_data=f"remove_item:{product_name}")])

    # Добавляем кнопки для управления корзиной
    keyboard.append([InlineKeyboardButton(text=get_message("buttons.add_comment", lang), callback_data="add_comment")])
    keyboard.append([InlineKeyboardButton(text=get_message("buttons.pay_online", lang), callback_data="pay_online")])
    keyboard.append([InlineKeyboardButton(text=get_message("buttons.pay_cash", lang), callback_data="pay_cash")])
    keyboard.append([InlineKeyboardButton(text=get_message("buttons.back", lang), callback_data="back_to_main")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇺🇿 O'zbekcha")],
        ],
        resize_keyboard=True
    )

def branch_keyboard(lang: str) -> InlineKeyboardMarkup:
    branches_data = get_message("branches", lang)
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=callback)]
        for name, callback in branches_data["options"]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)