import requests

def get_player_summary(username: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(f'https://api.chess.com/pub/player/{username}', headers=headers)
    
    data = response.json()
    
    summary = {}

    if 'player_id' in data:
        summary['pfp'] = data['avatar']
        summary['username'] = username
        summary['followers'] = data['followers']
        summary['location'] = data['location'] if 'location' in data else None

        flag_id = data['country'].split('/')[-1].lower()
        summary ['flag'] = f'https://flagcdn.com/64x48/{flag_id}.png'

        return summary
    else:
        return None