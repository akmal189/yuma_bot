from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from keyboards.menu_keyboards import categories_keyboard, cart_keyboard_with_delete
from aiogram.fsm.context import FSMContext
from keyboards.menu_keyboards import start_keyboard
from states.cart_state import CartState
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from config import ADMIN_ID

router = Router()

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone_number = data.get("phone_number")

    if phone_number:
        # Номер уже есть
        await message.answer("Добро пожаловать! 👋", reply_markup=start_keyboard())
    else:
        # Просим номер
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Поделиться номером", request_contact=True)]
            ],
            resize_keyboard=True
        )
        await message.answer(
            "Пожалуйста, поделитесь своим номером для оформления заказов:",
            reply_markup=keyboard
        )

@router.message(F.contact)
async def save_phone(message: types.Message, state: FSMContext, bot):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)

    # Отправляем админу
    #await bot.send_message(ADMIN_ID, f"📱 Новый номер клиента: {phone_number}")

    # Меню и корзина
    await message.answer(
        "Спасибо! Номер сохранён. Выберите действие:",
        reply_markup=start_keyboard()
    )

@router.callback_query(lambda c: c.data == "show_categories")
async def show_categories(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите категорию:", reply_markup=categories_keyboard())

@router.message(lambda message: message.text == "🍔 Меню")
async def show_categories(message: types.Message):
    await message.answer("Выберите категорию 🍽️:", reply_markup=categories_keyboard())

@router.message(lambda message: message.text == "🛒 Корзина")
async def show_cart_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    comment = data.get("comment", None)

    if cart:
        total = sum(item["price"] for item in cart)
        text = "🛒 Ваша корзина:\n" + "\n".join(
            f"- {item['name']} — {item['price']} сум" for item in cart
        )
        text += f"\n\n💰 Общая сумма: {total} сум"

        if comment:
            text += f"\n📝 Комментарий: {comment}"

        await message.answer(text, reply_markup=cart_keyboard_with_delete(cart))
    else:
        await message.answer("Ваша корзина пуста.")