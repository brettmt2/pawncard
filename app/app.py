import json
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis

from app.pawncard import get_player_summary

load_dotenv(override=False)

r: redis.Redis = None

@asynccontextmanager
async def lifespan(_: FastAPI):
    # load Redis manager
    global r
    r = redis.Redis(host='localhost', port=6379, db=0)

    yield

    r.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/summaries/{username}")
def get_summary(username: str):

    cached = r.get(f'summary/{username}')
    if cached:
        return json.loads(cached)

    data = get_player_summary(username=username)
    r.setex(f'summary/{username}', 30, json.dumps(data))
    
    return data

