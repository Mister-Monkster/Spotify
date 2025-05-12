import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand

from config import get_bot_token
from bot.service import TelegramService

from bot.router import router

service = TelegramService()

dp = Dispatcher(service=service)

bot = Bot(token=get_bot_token())



async def run_bot():
    dp.include_router(router)
    await bot.set_my_commands(
        commands=[
            BotCommand(command='start', description='Получение ссылки на авторизацию🌐'),
            BotCommand(command='logout', description='Выход из аккаунта Spotify🚪'),
            BotCommand(command='track', description='Информация о текущем треке🎵'),
            BotCommand(command='top_tracks', description='Топ треков за месяц🔝'),
            BotCommand(command='top_artists', description='Топ артистов за месяц🔝'),
            BotCommand(command='playlists', description='Твои плейлисты💿'),
        ]
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
