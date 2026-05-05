import json
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import httpx

from app.pawncard import get_player_summary

load_dotenv(override=False)

client: httpx.AsyncClient = None
r: redis.Redis = None

@asynccontextmanager
async def lifespan(_: FastAPI):
    # load the httpx context manager
    global client
    client = httpx.AsyncClient()

    # load Redis manager
    global r
    r = redis.Redis(host='localhost', port=6379, db=0)

    yield

    await client.aclose()
    r.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/summaries/{username}")
async def get_summary(username: str):

    cached = r.get(f'summary/{username}')
    if cached:
        return json.loads(cached)

    data = await get_player_summary(client=client, username=username)
    r.setex(f'summary/{username}', 30, json.dumps(data))
    
    return data

