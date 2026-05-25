import json
from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import redis
import httpx
import boto3

from app.pawncard import get_user_summary, get_user_feed
from app.analyze import analysis_engine

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
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', 6379))
    password = os.getenv('REDIS_PASSWORD', None)

    r = redis.Redis(host=host, port=port, password=password, decode_responses=True)

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
    allow_origins=["https://pawncard.up.railway.app"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/data/{username}")
async def get_user_data(username: str):
    data = {}

    if username:
        username = username.lower()
    else:
        username = 'hikaru'

    cached = r.get(f'summary/{username}')
    if cached:
        data['summary'] = json.loads(cached)
        data['feed'] = await get_user_feed(s3=s3, client=client, username=username, append=False)
        return data

    data['summary'] = await get_user_summary(client=client, username=username)
    data['feed'] = await get_user_feed(s3=s3, client=client, username=username, append=True)
    
    r.setex(f'summary/{username}', 120, json.dumps(data['summary']))
    
    return data

@app.get("/analysis/{username}/{game_id}")
async def analyze_game(username: str, game_id: str):
    engine = analysis_engine(s3=s3, username=username, game_id=game_id)
    res = engine.analyze()
    return res

app.mount("/", StaticFiles(directory="web", html=True), name="web")