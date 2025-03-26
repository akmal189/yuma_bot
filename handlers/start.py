from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from keyboards.menu_keyboards import categories_keyboard, cart_keyboard_with_delete, start_keyboard, language_keyboard
from aiogram.fsm.context import FSMContext
from states.cart_state import CartState
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from config import ADMIN_ID
from localization import get_message
from states.language_state import LanguageState
from data.products import products

router = Router()

# Модифицировать @router.message(CommandStart())
@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language")
    phone_number = data.get("phone_number")

    if lang and phone_number:
        # Если язык и телефон уже есть — сразу показываем главное меню
        await message.answer(get_message("menu.welcome", lang), reply_markup=start_keyboard(lang))
        return
    
    if not lang:
        # Если язык не выбран — предлагаем его выбрать
        await state.clear()
        await message.answer("Пожалуйста, выберите язык:\nIltimos tilni tanlang:", reply_markup=language_keyboard())
        await state.set_state(LanguageState.choose_language)
    else:
        # Если язык есть, но номера нет — просим номер
        await proceed_to_phone(message, state, lang)

async def proceed_to_phone(message: types.Message, state: FSMContext, lang: str):
    data = await state.get_data()
    phone_number = data.get("phone_number")

    if phone_number:
        # Если номер уже есть — сразу показываем главное меню
        await message.answer(get_message("menu.welcome", lang), reply_markup=start_keyboard(lang))
    else:
        # Просим номер телефона
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=get_message("menu.share_phone", lang), request_contact=True)]],
            resize_keyboard=True
        )
        await message.answer(get_message("menu.request_phone", lang), reply_markup=keyboard)

# Для русского
@router.message(LanguageState.choose_language, F.text == "🇷🇺 Русский")
async def set_language_ru(message: types.Message, state: FSMContext):
    await state.update_data(language="ru")
    await proceed_to_phone(message, state, "ru")

# Для узбекского
@router.message(LanguageState.choose_language, F.text == "🇺🇿 O'zbekcha")
async def set_language_uz(message: types.Message, state: FSMContext):
    await state.update_data(language="uz")
    await proceed_to_phone(message, state, "uz")

# Модифицировать @router.message(F.contact) — добавляем использование языка:
@router.message(F.contact)
async def save_phone(message: types.Message, state: FSMContext, bot):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)

    data = await state.get_data()
    lang = data.get("language", "ru")

    # Отправка приветствия с учетом языка
    await message.answer(get_message("menu.phone_saved", lang), reply_markup=start_keyboard(lang))

@router.callback_query(lambda c: c.data == "show_categories")
async def show_categories(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите категорию:", reply_markup=categories_keyboard())

@router.message(lambda message: message.text == "🍔 Меню" or message.text == "🍔 Menu")
async def show_categories(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")

    categories_list = products[lang].keys()

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=category, callback_data=f"category_{category}")]
            for category in categories_list
        ]
    )

    await message.answer(
        "Выберите категорию 🍽️:" if lang == "ru" else "Kategoriya tanlang 🍽️:",
        reply_markup=keyboard
    )


@router.message(lambda message: message.text in ["🛒 Корзина", "🛒 Savat"])
async def show_cart_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    cart = data.get("cart", {})
    comment = data.get("comment", None)

    cart_text = "🛒 Ваша корзина:\n\n" if lang == "ru" else "🛒 Sizning savatingiz:\n\n"
    total_price = 0

    if cart:
        for product, details in cart.items():
            quantity = details["quantity"]
            price = details["price"]
            total = quantity * price
            total_price += total
            cart_text += f"🔹 {product} — {quantity} шт. x {price} сум = {total} сум\n"

        cart_text += f"\n💰 Общая сумма: {total_price} сум" if lang == "ru" else f"\n💰 Jami: {total_price} sum"

        if comment:
            cart_text += f"\n📝 Комментарий: {comment}" if lang == "ru" else f"\n📝 Izoh: {comment}"

        await message.answer(cart_text, reply_markup=cart_keyboard_with_delete(cart, lang))
    else:
        await message.answer("🛒 Ваша корзина пуста!" if lang == "ru" else "🛒 Savatingiz boʻsh!")
