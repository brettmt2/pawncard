import os
import httpx
import json
from datetime import datetime
import asyncio

async def get_user_summary_stats(client: httpx.AsyncClient, username: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = await client.get(f'https://api.chess.com/pub/player/{username}/stats', headers=headers)

    data = response.json()

    game_types = [data.get('chess_rapid', None), data.get('chess_blitz', None), data.get('chess_bullet', None)]
    stats = {}

    for key, game_type in zip(['rapid', 'blitz', 'bullet'], game_types):
        stats[key] = {}

        if game_type is None:
            stats[key] = None
            continue # player hasn't played this format

        curr = game_type['last']['rating']

        # make peak = curr if no peak (usually from unregistered ratings and new accounts)
        peak = game_type.get('best', None)

        if peak:
            peak = peak.get('rating')
        else:
            peak = curr

        record = f'{game_type['record']['win']} - {game_type['record']['loss']} - {game_type['record']['draw']}'

        stats[key]['curr_rating'] = curr
        stats[key]['peak_rating'] = peak
        stats[key]['record'] = record

    return stats

async def get_user_summary(client: httpx.AsyncClient, username: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = await client.get(f'https://api.chess.com/pub/player/{username}', headers=headers)
    
    data = response.json()
    
    summary = {}

    # no player id if inexistent username entered
    if 'player_id' in data:
        summary['pfp'] = data.get('avatar', 'https://www.chess.com/bundles/web/images/user-image.007dad08.svg')
        summary['username'] = username
        summary['followers'] = data['followers']
        summary['location'] = data['location'] if 'location' in data else None

        flag_id = data['country'].split('/')[-1].lower()
        if flag_id != 'xx':
            summary['flag'] = f'https://flagcdn.com/64x48/{flag_id}.png'
        else:
            summary['flag'] = 'https://flagcdn.com/64x48/un.png'

        summary['stats'] = await get_user_summary_stats(client=client, username=username)

        return summary
    else:
        return None
    

async def append_feed(feed: list, client: httpx.AsyncClient, username: str):
    if feed is None:
        feed = []
    
    now = datetime.now()
    url = f'https://api.chess.com/pub/player/{username}/games/{now.year}/{now.month:02d}'

    username = username.lower() if username else None
    if username is None:
        return

    headers = {'User-Agent': 'Mozilla/5.0'}
    result = await client.get(url, headers=headers)

    data = result.json()
    games: list = data.get('games', [])
    games = games[-3:]

    if not games:
        return feed
    
    # don't add existing feed ID
    feed_ids = [d.get('feed_id', -1) for d in feed]

    # get the most recent win and append to feed
    for game in games:
        feed_item = {}
        game_id = game['url'].split('/')[-1]

        if game_id in feed_ids:
            continue

        white = game['white']
        black = game['black']

        white_username = white['username'].lower()
        black_username = black['username'].lower()

        if (white['result'] == 'win' and white_username == username) \
            or (black['result'] == 'win' and black_username == username):
            
            feed_item['fen'] = game.get('fen', None)
            feed_item['pgn'] = game.get('pgn', None)

            feed_item['time_class'] = game['time_class']

            if white['result'] == 'win':
                feed_item['new_rating'] = white['rating']
                feed_item['win_color'] = 'white'
                feed_item['opponent'] = {'username': black['username'], 'rating': black['rating']}
                feed_item['win_condition'] = black['result']

            if black['result'] == 'win':
                feed_item['new_rating'] = black['rating']
                feed_item['win_color'] = 'black'
                feed_item['opponent'] = {'username': white['username'], 'rating': white['rating']}
                feed_item['win_condition'] = white['result']

            feed_item['accuracies'] = game.get('accuracies', None)

            feed_item['feed_id'] = game_id

        if feed_item:
            feed.append(feed_item)

    return feed

async def get_user_feed(s3, client: httpx.AsyncClient, username: str, append: bool = True):
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

        # don't create an s3 object if there is no feed
        if updated_feed is not None and len(updated_feed) > 0:
                        
            # keep feed at 10 most recent games
            updated_feed = updated_feed[-10:]

            s3.put_object(
                Bucket=os.getenv('FEEDS_BUCKET_NAME'),
                Key=f'feeds/{username}',
                Body=json.dumps(updated_feed)
            )

        return updated_feed

    return feed