import json
import os
from stockfish import Stockfish

class analysis_engine:
    def __init__(self, sf: Stockfish, s3, username: str, game_id: str):
        self.sf = sf
        self.s3 = s3
        self.username = username
        self.game_id = game_id

    def get_pgn(self):
        response = self.s3.get_object(Bucket=os.getenv('FEEDS_BUCKET_NAME'), Key=f'feeds/{self.username}')
        feed_content = json.loads(response['Body'].read().decode('utf-8'))
        
        pgn = None
        for f in feed_content:
            if f['feed_id'] == self.game_id:
                pgn = f['pgn'] if f['pgn'] else None

        return pgn

    def analyze_pgn(self, pgn):
        return ['test', pgn[:10]]

    def analyze(self):
        pgn = self.get_pgn()

        if pgn:
            response = self.analyze_pgn(pgn)
        else: # the game id from chesscom needs to be already analyzed on their server for a pgn to be in the body
            response = None

        return response
    
    def version(self):
        return self.sf.get_stockfish_major_minor_version()