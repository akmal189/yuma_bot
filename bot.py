import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers import start, menu, cart

router = Router()  # Глобальный роутер

@router.callback_query()
async def catch_all_callbacks(callback: types.CallbackQuery):
    print(f"🔍 Callback получен: {callback.data}")  # Логируем ВСЕ callback-запросы

async def main():
    bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Включаем все роутеры, включая глобальный router
    dp.include_routers(start.router, menu.router, cart.router, router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    print("🚀 Бот запущен!")
    asyncio.run(main())
