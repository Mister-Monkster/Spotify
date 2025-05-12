import asyncio
import uvicorn
from fastapi import FastAPI

from bot.bot import run_bot
from spotify.router import router as spotify_router

app = FastAPI()

app.include_router(spotify_router)

if __name__ == '__main__':
    uvicorn.run(app)

