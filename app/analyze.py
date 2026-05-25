import json
import os
import re
import chess
import chess.pgn
import chess.engine
import io

class analysis_engine:
    def __init__(self, s3, username: str, game_id: str):
        self.s3 = s3
        self.username = username
        self.game_id = game_id

    def clean_pgn(self, pgn: str):
        headers = {"Event", "Site", "Date", "Round", "White", "Black", "Result"}

        header_lines = []
        for line in pgn.splitlines():
            match = re.match(r'^\[(\w+)\s+".*"\]$', line)
            if match and match.group(1) in headers:
                header_lines.append(line)
        
        moves_section = pgn.split("\n\n", 1)[1].strip()

        # remove clock
        moves_clean = re.sub(r'\s*\{[^}]*\}', '', moves_section)

        # remove the ... from black's moves
        moves_clean = re.sub(r'\d+\.\.\.', '', moves_clean)

        # remove extra whitespace
        moves_clean = re.sub(r' +', ' ', moves_clean).strip()

        pgn = "\n".join(header_lines) + "\n\n" + moves_clean

        return pgn

    def get_pgn(self):
        response = self.s3.get_object(Bucket=os.getenv('FEEDS_BUCKET_NAME'), Key=f'feeds/{self.username}')
        feed_content = json.loads(response['Body'].read().decode('utf-8'))
        
        pgn = None
        for f in feed_content:
            if f['feed_id'] == self.game_id:
                pgn = f['pgn'] if f['pgn'] else None

        return self.clean_pgn(pgn)

    def analyze_pgn(self, pgn):
        game = chess.pgn.read_game(io.StringIO(pgn))
        board = game.board()
        evaluations = []
        stockfish_path = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")

        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            for move in game.mainline_moves():
                san = board.san(move)
                move_number = board.fullmove_number
                color = "white" if board.turn == chess.WHITE else "black"
                board.push(move)
                info = engine.analyse(board, chess.engine.Limit(depth=12))
                
                score_obj = info["score"].white()

                if score_obj.is_mate():
                    score = f"M{score_obj.mate()}"
                else:
                    score = round(score_obj.score() / 100, 2)

                evaluations.append({
                    "move_number": move_number,
                    "color": color,
                    "move": san,
                    "score": score
                })

        return evaluations
    
    def eval_result(evaluations: list):
        pass

    def analyze(self):
        pgn = self.get_pgn()

        if pgn:
            evals = self.analyze_pgn(pgn)
            response = self.eval_result(evals)
        else: # the game id from chesscom needs to be already analyzed on their server for a pgn to be in the body
            response = None

        return response