from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.menu_keyboards import categories_keyboard, main_menu_keyboard, cart_keyboard_with_delete
from config import ADMIN_ID

router = Router()

@router.callback_query(lambda c: c.data == "show_cart")
async def inline_show_cart(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])

    if cart:
        total = sum(item["price"] for item in cart if "price" in item)
        text = "🛒 Ваша корзина:\n"
        for item in cart:
            text += f"- {item['name']} — {item['price']} сум\n"
        text += f"\n💰 <b>Итого: {total} сум</b>"
        await callback.message.edit_text(text, reply_markup=cart_keyboard_with_delete(cart), parse_mode="HTML")
    else:
        await callback.message.edit_text("Ваша корзина пуста!", reply_markup=main_menu_keyboard())

@router.callback_query(lambda c: c.data.startswith("remove_item:"))
async def remove_item(callback: types.CallbackQuery, state: FSMContext):
    index = int(callback.data.split(":")[1])
    data = await state.get_data()
    cart = data.get("cart", [])
    
    if 0 <= index < len(cart):
        removed_item = cart.pop(index)
        await state.update_data(cart=cart)
        await callback.answer(f"Удалено: {removed_item['name']}")
    else:
        await callback.answer("Ошибка удаления")
    
    # Показываем обновлённую корзину
    if cart:
        total = sum(item["price"] for item in cart)
        text = "🛒 Ваша корзина:\n"
        for item in cart:
            text += f"- {item['name']} — {item['price']} сум\n"
        text += f"\n💰 <b>Итого: {total} сум</b>"
        await callback.message.edit_text(text, reply_markup=cart_keyboard_with_delete(cart), parse_mode="HTML")
    else:
        await callback.message.edit_text("Ваша корзина пуста!", reply_markup=main_menu_keyboard())

@router.callback_query(lambda c: c.data == "pay_online")
async def pay_online(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("💳 Ссылка на оплату: https://example.com/pay")
    await send_order_to_admin(callback, state)

@router.callback_query(lambda c: c.data == "pay_cash")
async def pay_cash(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Вы выбрали оплату при получении. Спасибо за заказ!")
    await send_order_to_admin(callback, state)

@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите действие:", reply_markup=main_menu_keyboard())

async def send_order_to_admin(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", [])
    if not cart:
        return
    
    total = sum(item["price"] for item in cart)
    comment = data.get("comment", "Нет комментария.")
    phone = data.get("phone_number", "Не указан")
    order_text = f"📢 Новый заказ от {callback.from_user.first_name}, @{callback.from_user.username}:\n"
    order_text += f"\n📞 Телефон: {phone}\n"
    for item in cart:
        order_text += f"- {item['name']} — {item['price']} сум\n"

    order_text += f"\n📝 Комментарий: {comment}"
    order_text += f"\n💰 Итого: {total} сум"
    
    await callback.bot.send_message(chat_id=ADMIN_ID, text=order_text)
    await state.update_data(cart=[])  # Очищаем корзину


class CartStates(StatesGroup):
    waiting_for_comment = State()


@router.callback_query(lambda c: c.data == "add_comment")
async def ask_comment(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите комментарий к заказу:")
    await state.set_state(CartStates.waiting_for_comment)

@router.message(CartStates.waiting_for_comment)
async def save_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)

    data = await state.get_data()
    cart = data.get("cart", [])
    total = sum(item["price"] for item in cart) if cart else 0

    text = "🛒 Ваша корзина:\n"
    if cart:
        for index, item in enumerate(cart):
            text += f"{index+1}. {item['name']} — {item['price']}₽\n"
        text += f"\n💰 Итого: {total}₽"
    else:
        text += "\nПусто."

    await message.answer("Комментарий сохранён! 📝")
    await message.answer(text, reply_markup=cart_keyboard_with_delete(cart))
    await state.set_state(None)  # Возвращаемся в состояние по умолчанию

async def update_cart(state: FSMContext, item: dict):
    data = await state.get_data()
    cart = data.get("cart", [])
    cart.append({
        "name": item["name"],
        "price": item["price"]
    })
    await state.update_data(cart=cart)