# app/rate_limiter.py
import redis.asyncio as redis_lib
from fastapi import Request, HTTPException
from dotenv import load_dotenv
import os
RATE_LIMIT = 5  # max requests
WINDOW_SECONDS = 60  # time window in seconds

load_dotenv()

async def init_redis(app):
    # redis_client = redis_lib.Redis(host='localhost', port=6379, decode_responses=True)
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")  # fallback for local dev
    redis_client = redis_lib.from_url(redis_url, decode_responses=True)
    app.state.redis = redis_client

async def rate_limiter(request: Request):
    redis = request.app.state.redis
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]
    key = f"rate-limit:{token}"

    current = await redis.get(key)

    if current is None:
        await redis.set(key, 1, ex=WINDOW_SECONDS)
    elif int(current) < RATE_LIMIT:
        await redis.incr(key)
    else:
        ttl = await redis.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {ttl} seconds."
        )