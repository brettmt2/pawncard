import json
import os

def get_pgn(s3, username: str, game_id: str):
    response = s3.get_object(Bucket=os.getenv('FEEDS_BUCKET_NAME'), Key=f'feeds/{username}')
    feed_content = json.loads(response['Body'].read().decode('utf-8'))
    
    pgn = None
    for f in feed_content:
        if f['feed_id'] == game_id:
            pgn = f['pgn'] if f['pgn'] else None

    return pgn

def analyze_pgn(pgn):
    return ['test', pgn[:10]]

def analyze(s3, username: str, game_id: str):
    pgn = get_pgn(s3=s3, username=username, game_id=game_id)

    if pgn:
        response = analyze_pgn(pgn)
    else: # the game id from chesscom needs to be already analyzed on their server for a pgn to be in the body
        response = None

    return response

