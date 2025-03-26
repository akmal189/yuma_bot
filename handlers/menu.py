from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from keyboards.menu_keyboards import products_keyboard, categories_keyboard, main_menu_keyboard
from states.cart_state import CartState
from data.products import products



router = Router()

@router.callback_query(lambda c: c.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")  # Получаем язык пользователя
    category_key = callback.data.replace("category_", "")  # Убираем префикс

    if category_key not in products[lang]:
        await callback.answer("Ошибка: категория не найдена!" if lang == "ru" else "Xatolik: kategoriya topilmadi!")
        return

    items = products[lang][category_key]  # Получаем товары категории
    # Формируем список кнопок товаров
    keyboard_buttons = [
        [types.InlineKeyboardButton(text=item, callback_data=f"product_{item}")]
        for item in items.keys()
    ]
    # Добавляем кнопку "🔙 Назад"
    keyboard_buttons.append([types.InlineKeyboardButton(text="🔙 Назад" if lang == "ru" else "🔙 Orqaga", callback_data="back_to_categories")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    # Удаляем старое сообщение (если было фото)
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"⚠ Ошибка удаления сообщения: {e}")

    await callback.message.answer(
        f"Товары в категории {category_key}:" if lang == "ru" else f"{category_key} dagi mahsulotlar:",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data.startswith("product_"))
async def show_product_details(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")  # Получаем язык пользователя

    product_name = callback.data.replace("product_", "")
    category_name = None

    for category, items in products[lang].items():
        if product_name in items:
            category_name = category
            break

    if not category_name:
        await callback.answer("Ошибка: товар не найден!" if lang == "ru" else "Xatolik: mahsulot topilmadi!")
        return

    product = products[lang][category_name][product_name]
    price = product["price"]
    photo = product.get("photo", None)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🛒 Добавить в корзину" if lang == "ru" else "🛒 Savatga qoʻshish", callback_data=f"add_to_cart_{product_name}")],
        [types.InlineKeyboardButton(text="🔙 Назад" if lang == "ru" else "🔙 Orqaga", callback_data=f"category_{category_name}")]
    ])

    # Удаляем предыдущее сообщение
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"⚠ Ошибка удаления сообщения: {e}")

    # Отправляем фото товара или текст, если фото нет
    if photo:
        await callback.message.answer_photo(
            photo=photo,
            caption=f"<b>{product_name}</b>\n💰 Цена: {price} сум" if lang == "ru" else f"<b>{product_name}</b>\n💰 Narxi: {price} so'm",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            f"<b>{product_name}</b>\n💰 Цена: {price} сум" if lang == "ru" else f"<b>{product_name}</b>\n💰 Narxi: {price} so'm",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@router.callback_query(lambda c: c.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")  # Получаем язык пользователя

    categories_list = products[lang].keys()

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=category, callback_data=f"category_{category}")]
            for category in categories_list
        ]
    )

    await callback.message.edit_text(
        "Выберите категорию 🍽️:" if lang == "ru" else "Kategoriya tanlang 🍽️:",
        reply_markup=keyboard
    )

@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")
    await callback.message.edit_text("Выберите действие:" if lang == "ru" else "Amalni tanlang:", reply_markup=main_menu_keyboard(lang))


@router.callback_query(lambda c: c.data.startswith("add_to_cart_"))
async def add_to_cart(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "ru")

    product_name = callback.data.replace("add_to_cart_", "")

    # Ищем товар в категориях
    category_name = None
    for category, items in products[lang].items():
        if product_name in items:
            category_name = category
            break

    if not category_name:
        await callback.answer("Ошибка: товар не найден!" if lang == "ru" else "Xatolik: mahsulot topilmadi!")
        return

    # Получаем текущую корзину
    cart = data.get("cart", {})

    # Добавляем товар в корзину
    if product_name in cart:
        cart[product_name]["quantity"] += 1
    else:
        cart[product_name] = {
            "quantity": 1,
            "price": products[lang][category_name][product_name]["price"]
        }

    # Сохраняем обновленные данные
    await state.update_data(cart=cart)

    await callback.answer("✅ Товар добавлен в корзину!" if lang == "ru" else "✅ Mahsulot savatga qoʻshildi!")
