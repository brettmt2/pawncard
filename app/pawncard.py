import os
import httpx
import json
from datetime import datetime
import asyncio

async def get_player_summary_stats(client: httpx.AsyncClient, username: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = await client.get(f'https://api.chess.com/pub/player/{username}/stats', headers=headers)

    data = response.json()

    game_types = [data['chess_rapid'], data['chess_blitz'], data['chess_bullet']]
    stats = {}

    for key, game_type in zip(['rapid', 'blitz', 'bullet'], game_types):
        stats[key] = {}

        if not game_type:
            continue # player hasn't played this format

        curr = game_type['last']['rating']
        peak = game_type['best']['rating']
        record = f'{game_type['record']['win']} - {game_type['record']['loss']} - {game_type['record']['draw']}'

        stats[key]['curr_rating'] = curr
        stats[key]['peak_rating'] = peak
        stats[key]['record'] = record

    return stats

async def get_player_summary(client: httpx.AsyncClient, username: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = await client.get(f'https://api.chess.com/pub/player/{username}', headers=headers)
    
    data = response.json()
    
    summary = {}

    if 'player_id' in data:
        summary['pfp'] = data['avatar']
        summary['username'] = username
        summary['followers'] = data['followers']
        summary['location'] = data['location'] if 'location' in data else None

        flag_id = data['country'].split('/')[-1].lower()
        summary ['flag'] = f'https://flagcdn.com/64x48/{flag_id}.png'

        summary['stats'] = await get_player_summary_stats(client=client, username=username)

        return summary
    else:
        return None
    

async def append_feed(feed: list, client: httpx.AsyncClient, username: str):
    feed_item = {}
    now = datetime.now()
    url = f'https://api.chess.com/pub/player/{username}/games/{now.year}/{now.month:02d}'

    headers = {'User-Agent': 'Mozilla/5.0'}
    result = await client.get(url, headers=headers)

    data = result.json()
    games: list = data.get('games', [])
    games.reverse() # LIFO

    if not games:
        return feed
    
    # get the most recent win and append to feed
    for game in games:
        white = game['white']
        black = game['black']

        if (white['result'] == 'win' and white['username'] == username) \
            or (black['result'] == 'win' and black['username'] == username):

            feed_item['pgn'] = game['pgn']

            feed_item['time_class'] = game['time_class']

            if white['result'] == 'win':
                feed_item['win_color'] = 'white'
                feed_item['opponent'] = {'username': black['username'], 'rating': black['rating']}
                feed_item['win_condition'] = black['result']

            if black['result'] == 'win':
                feed_item['win_color'] = 'black'
                feed_item['opponent'] = {'username': white['username'], 'rating': white['rating']}
                feed_item['win_condition'] = white['result']

            feed_item['accuracies'] = game['accuracies']
            
            break

    if feed_item and feed is not None:
        feed.append(feed_item)
        
    if feed_item and feed is None:
        feed = [feed_item]

    return feed

async def get_player_feed(s3, client: httpx.AsyncClient, username: str, append: bool = True):
    paginator = s3.get_paginator('list_objects_v2')
    feed = None

    for page in paginator.paginate(Bucket=os.getenv('FEEDS_BUCKET_NAME'), Prefix='feeds/'):
        keys = [obj['Key'] for obj in page.get('Contents', [])]

        if f'feeds/{username}' in keys:
            print('feed already exists! getting it from s3 ~')
            obj = s3.get_object(Bucket=os.getenv('FEEDS_BUCKET_NAME'), Key=f'feeds/{username}')
            feed = json.loads(obj['Body'].read().decode('utf-8'))

            break
    
    if append:
        updated_feed = await append_feed(feed=feed, client=client, username=username)

        s3.put_object(
            Bucket=os.getenv('FEEDS_BUCKET_NAME'),
            Key=f'feeds/{username}',
            Body=json.dumps(updated_feed)
        )

        return updated_feed

    return feed

if __name__ == "__main__":
    async def main():
        async with httpx.AsyncClient() as client:
            res = await append_feed(None, client, "peach_02")
            print(res)
    
    asyncio.run(main())