import json

def analyze_pgn(username: str, game_id: str):
    pass

def get_pgn(s3, username: str, game_id: str):
    response = s3.get_object(Bucket='your-bucket-name', Key=username)
    feed_content = json.loads(response['Body'].read().decode('utf-8'))