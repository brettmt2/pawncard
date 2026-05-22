import json
import os

def get_pgn(s3, username: str, game_id: str):
    response = s3.get_object(Bucket=os.getenv('FEEDS_BUCKET_NAME'), Key=username)
    feed_content = json.loads(response['Body'].read().decode('utf-8'))
    
    pgn = None
    for f in feed_content:
        if f['feed_id'] == game_id:
            pgn = f['pgn'] if f['pgn'] else None

    return pgn


def analyze_pgn(pgn: str):
    pass