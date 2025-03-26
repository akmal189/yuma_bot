from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.menu_keyboards import main_menu_keyboard, cart_keyboard_with_delete, branch_keyboard
from config import ADMIN_ID, BRANCH_ADMINS
from states.cart_state import CartState, OrderState
from localization import get_message, get_branch_name

router = Router()


# 📌 Состояние для комментария
class CartStates(StatesGroup):
    waiting_for_comment = State()
    waiting_for_branch = State()


# 📌 Показать корзину (callback)
@router.callback_query(lambda c: c.data == "show_cart")
async def inline_show_cart(callback: types.CallbackQuery, state: FSMContext):
    print(f"Callback: {callback.data}")  # Логируем callback

    data = await state.get_data()
    lang = data.get("language", "ru")
    cart = data.get("cart", {})

    if cart:
        cart_text = get_message("cart.your_cart", lang) + "\n\n"
        total_price = 0

        for product, details in cart.items():
            quantity = details["quantity"]
            price = details["price"]
            total = quantity * price
            total_price += total
            cart_text += f"🔹 {product} — {quantity} x {price} сум = {total} сум\n"

        cart_text += f"\n💰 <b>{get_message('cart.total', lang)}: {total_price} сум</b>"
        await callback.message.edit_text(cart_text, reply_markup=cart_keyboard_with_delete(cart, lang), parse_mode="HTML")
    else:
        await callback.message.edit_text(get_message("cart.empty", lang), reply_markup=main_menu_keyboard())


# 📌 Удаление товара из корзины (callback)
@router.callback_query(lambda c: c.data.startswith("remove_item:"))
async def remove_item(callback: types.CallbackQuery, state: FSMContext):
    print(f"Callback: {callback.data}")  # Логируем callback

    item_name = callback.data.split(":")[1]
    data = await state.get_data()
    cart = data.get("cart", {})

    if item_name in cart:
        del cart[item_name]
        await state.update_data(cart=cart)
        await callback.answer(get_message("cart.removed", "ru").format(item=item_name))
    else:
        await callback.answer(get_message("cart.remove_error", "ru"))

    # Обновляем корзину
    if cart:
        total = sum(details["quantity"] * details["price"] for details in cart.values())
        cart_text = get_message("cart.your_cart", "ru") + "\n\n"

        for product, details in cart.items():
            cart_text += f"🔹 {product} — {details['quantity']} x {details['price']} сум\n"

        cart_text += f"\n💰 <b>{get_message('cart.total', 'ru')}: {total} сум</b>"
        await callback.message.edit_text(cart_text, reply_markup=cart_keyboard_with_delete(cart, "ru"), parse_mode="HTML")
    else:
        await callback.message.edit_text(get_message("cart.empty", "ru"), reply_markup=main_menu_keyboard())


# 📌 Кнопка "Добавить комментарий"
@router.callback_query(lambda c: c.data == "add_comment")
async def ask_comment(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")

    await callback.message.answer(get_message("cart.enter_comment", lang))  # "Введите ваш комментарий:"
    await state.set_state(CartStates.waiting_for_comment)


# 📌 Обработчик комментария (message)
@router.message(CartStates.waiting_for_comment)
async def save_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")

    await state.update_data(comment=message.text)
    await message.answer(get_message("cart.comment_saved", "ru"))

    data = await state.get_data()
    cart = data.get("cart", {})

    if cart:
        cart_text = get_message("cart.your_cart", "ru") + "\n\n"
        for product, details in cart.items():
            cart_text += f"🔹 {product} — {details['quantity']} x {details['price']} сум\n"

        total = sum(details["quantity"] * details["price"] for details in cart.values())
        cart_text += f"\n💰 <b>{get_message('cart.total', 'ru')}: {total} сум</b>"

        await message.answer(cart_text, reply_markup=cart_keyboard_with_delete(cart, lang), parse_mode="HTML")

    #await state.clear()  # Сбрасываем состояние
    await state.set_state(None)


# 📌 Кнопка "Оплатить онлайн" (callback)
@router.callback_query(lambda c: c.data == "pay_online")
async def pay_online(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await callback.message.answer("💳 Оплата онлайн пока недоступна.")
    await send_order_to_admin(callback, state, lang)


# 📌 Кнопка "Оплата при получении" (callback)
@router.callback_query(lambda c: c.data == "pay_cash")
async def pay_cash(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await callback.message.answer(get_message("cart.choose_branch", lang), reply_markup=branch_keyboard(lang))
    await state.set_state(CartStates.waiting_for_branch)

@router.callback_query(CartStates.waiting_for_branch)
async def choose_branch(callback: types.CallbackQuery, state: FSMContext):
    branch = callback.data
    await state.update_data(branch=branch)
    lang = (await state.get_data()).get("language", "ru")

    await callback.message.answer(get_message("cart.payment_cash_confirmed", lang))
    await send_order_to_admin(callback, state, lang)
    await send_order_to_user(callback, state, lang)

# 📌 Отправка заказа админу
async def send_order_to_admin(callback: types.CallbackQuery, state: FSMContext, lang: str):
    data = await state.get_data()
    cart = data.get("cart", {})
    branch = data.get("branch", get_message("cart.no_branch", lang))

    branch_id = branch
    user_language = lang
    branch_name = get_branch_name(branch_id, user_language)
    admin_id = BRANCH_ADMINS.get(branch_id)

    if not admin_id:
        await callback.message.answer("Ошибка: Не найден администратор для данного филиала.")
        return
    
    if not cart:
        return

    total = sum(details["quantity"] * details["price"] for details in cart.values())
    comment = data.get("comment", get_message("cart.no_comment", lang))
    phone = data.get("phone_number", get_message("cart.no_phone", lang))

    order_text = f"📢 {get_message('cart.new_order', lang)} {callback.from_user.first_name}, @{callback.from_user.username}:\n"
    order_text += f"\n📞 {get_message('cart.phone', lang)}: {phone}\n"
    order_text += f"🏬 {get_message('cart.branch', lang)}: {branch_name}\n"

    for product, details in cart.items():
        order_text += f"- {product} — {details['quantity']} x {details['price']} {get_message('cart.currency', lang)}\n"

    order_text += f"\n📝 {get_message('cart.comment', lang)}: {comment}"
    order_text += f"\n💰 {get_message('cart.total', lang)}: {total} {get_message('cart.currency', lang)}"

    await callback.bot.send_message(chat_id=admin_id, text=order_text)

# 📌 Отправка заказа пользователю
async def send_order_to_user(callback: types.CallbackQuery, state: FSMContext, lang: str):
    data = await state.get_data()
    cart = data.get("cart", {})
    branch = data.get("branch", get_message("cart.no_branch", lang))

    branch_id = branch
    user_language = lang
    branch_name = get_branch_name(branch_id, user_language)

    if not cart:
        return

    total = sum(details["quantity"] * details["price"] for details in cart.values())
    comment = data.get("comment", get_message("cart.no_comment", lang))
    phone = data.get("phone_number", get_message("cart.no_phone", lang))

    user_order_text = f"✅ {get_message('cart.success_full', lang)}\n\n"
    user_order_text += f"🏬 {get_message('cart.branch', lang)}: {branch_name}\n"
    user_order_text += "\n".join([f"- {product} — {details['quantity']} x {details['price']} {get_message('cart.currency', lang)}"
                                  for product, details in cart.items()])
    user_order_text += f"\n\n📝 {get_message('cart.comment', lang)}: {comment}"
    user_order_text += f"\n💰 {get_message('cart.total', lang)}: {total} {get_message('cart.currency', lang)}"

    await callback.bot.send_message(chat_id=callback.from_user.id, text=user_order_text)
    await state.update_data(cart={})

# 📌 Кнопка "Назад" в корзине (callback)
@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(get_message("menu.choose_action", "ru"), reply_markup=main_menu_keyboard())