import requests
import httpx

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