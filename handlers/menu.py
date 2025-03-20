from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from keyboards.menu_keyboards import products_keyboard, categories_keyboard, main_menu_keyboard
from states.cart_state import CartState
from data.products import products

router = Router()

@router.callback_query(lambda c: c.data.startswith("category:"))
async def show_products(callback: types.CallbackQuery):
    category = callback.data.split(":")[1]
    for product_name, info in products[category].items():
        if info.get("photo"):
            await callback.message.answer_photo(
                photo=info["photo"],
                caption=f"{product_name} — {info['price']} сум"
            )
        else:
            await callback.message.answer(f"{product_name} — {info['price']} сум")
    await callback.message.answer("Выберите товар:", reply_markup=products_keyboard(category))

@router.callback_query(lambda c: c.data.startswith("product:"))
async def add_to_cart(callback: types.CallbackQuery, state: FSMContext):
    product_name = callback.data.split(":")[1]
    
    # Находим цену
    for category, items in products.items():
        if product_name in items:
            price = items[product_name]
            break
    
    data = await state.get_data()
    cart = data.get("cart", [])
    cart.append({"name": product_name, "price": price['price']})
    await state.update_data(cart=cart)
    
    await callback.answer(f"{product_name} добавлен в корзину!")

@router.callback_query(lambda c: c.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите категорию:", reply_markup=categories_keyboard())

@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите действие:", reply_markup=main_menu_keyboard())

