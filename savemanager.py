import sqlite3
import json
import os

class SaveManager:
    DB_FILE = "cosmic.db"

    @staticmethod
    def init_db():
        with sqlite3.connect(SaveManager.DB_FILE) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT,
                    start_time TEXT,
                    board_width INTEGER,
                    board_length INTEGER,
                    round_number INTEGER,
                    current_player TEXT,
                    winner TEXT,
                    player_exposed_cells TEXT,
                    enemy_exposed_cells TEXT,
                    actions TEXT
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS ships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER,
                    owner TEXT,
                    type TEXT,
                    position_x INTEGER,
                    position_y INTEGER,
                    orientation TEXT,
                    hit_cells TEXT,
                    spc_useable INTEGER,
                    emp_turns INTEGER,
                    FOREIGN KEY (game_id) REFERENCES games(id)
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS asteroids (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER,
                    owner TEXT,
                    x INTEGER,
                    y INTEGER,
                    direction TEXT,
                    FOREIGN KEY (game_id) REFERENCES games(id)
                )
            """)

    @staticmethod
    def save_game(game):
        SaveManager.init_db()
        with sqlite3.connect(SaveManager.DB_FILE) as con:
            cur = con.execute("""
                INSERT INTO games (player_name, start_time, board_width, board_length,
                    round_number, current_player, winner, player_exposed_cells, 
                    enemy_exposed_cells, actions)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                game.player.nickname,
                game.start_time,
                game.width,
                game.length,
                game.round_number,
                game.current_player,
                game.winner,
                json.dumps({f"{k[0]},{k[1]}": v for k, v in game.player_exposed_cells.items()}),
                json.dumps({f"{k[0]},{k[1]}": v for k, v in game.enemy_exposed_cells.items()}),
                json.dumps(game.actions)
            ))
            game_id = cur.lastrowid

            for owner, ships in [("player", game.player.ships), ("enemy", game.enemy.ships)]:
                for ship in ships:
                    con.execute("""
                        INSERT INTO ships (game_id, owner, type, position_x, position_y,
                            orientation, hit_cells, spc_useable, emp_turns)
                        VALUES (?,?,?,?,?,?,?,?,?)
                    """, (
                        game_id,
                        owner,
                        ship.__class__.__name__,
                        ship.ShipPoint[0],
                        ship.ShipPoint[1],
                        ship.orientation.name,
                        json.dumps(list(ship.hit_cells)),
                        1 if getattr(ship, "SpcUseable", True) else 0,
                        ship.emp_turns
                    ))

            for owner, asteroids in [("player", game.player.asteroids), ("enemy", game.enemy.asteroids)]:
                for asteroid in asteroids:
                    con.execute("""
                        INSERT INTO asteroids (game_id, owner, x, y, direction)
                        VALUES (?,?,?,?,?)
                    """, (
                        game_id,
                        owner,
                        asteroid.x,
                        asteroid.y,
                        json.dumps(asteroid.direction)
                    ))

        return game_id

    @staticmethod
    def load_saves():
        SaveManager.init_db()
        with sqlite3.connect(SaveManager.DB_FILE) as con:
            con.row_factory = sqlite3.Row
            rows = con.execute("""
                SELECT id, player_name, start_time, board_width, board_length, winner
                FROM games ORDER BY id DESC
            """).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def load_game(game_id):
        SaveManager.init_db()
        with sqlite3.connect(SaveManager.DB_FILE) as con:
            con.row_factory = sqlite3.Row
            game_row = con.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
            ships = con.execute("SELECT * FROM ships WHERE game_id=?", (game_id,)).fetchall()
            asteroids = con.execute("SELECT * FROM asteroids WHERE game_id=?", (game_id,)).fetchall()
        return dict(game_row), [dict(s) for s in ships], [dict(a) for a in asteroids]