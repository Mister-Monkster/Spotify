from typing import Annotated

from fastapi.params import Depends
from redis.asyncio import Redis

from spotify.service import SpotifyService



async def get_redis():
    redis = Redis.from_url("redis://localhost:6379",
                           decode_responses=True)
    try:
        yield redis
    finally:
        await redis.aclose()

RedisDep = Annotated[Redis, Depends(get_redis)]

async def get_service(redis: RedisDep):
    return SpotifyService(redis)

ServiceDep = Annotated[SpotifyService, Depends(get_service)]