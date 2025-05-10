import asyncio

from aiogram import Dispatcher, Bot

from service import TelegramService
from config import get_bot_token
from router import router

service = TelegramService()

dp = Dispatcher(service=service)

bot = Bot(token=get_bot_token())


async def run_bot():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
