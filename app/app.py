import json
from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import httpx
import boto3

from app.pawncard import get_player_summary, get_player_feed

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

    global s3
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

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

@app.get("/feeds/{username}")
async def get_feed(username: str):

    data = await get_player_feed(s3=s3, client=client, username=username)
    
    return data

