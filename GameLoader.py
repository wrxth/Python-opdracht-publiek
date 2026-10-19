import json
from savemanager import SaveManager
from Ships.Orientation import orientation

class GameLoader:
    def __init__(self, game):
        self.game = game

    def save(self):
        SaveManager.save_game(self.game)

    def load(self, game_id):
        from Ships.Kruiser import Kruiser
        from Ships.Jager import Jager
        from Ships.Slagschip import Slagschip
        from Ships.Verkenner import Verkenner
        from Ships.Commandoschip import Commandoschip
        from Asteroid import Asteroid

        ship_classes = {
            "Kruiser": Kruiser, "Jager": Jager, "Slagschip": Slagschip,
            "Verkenner": Verkenner, "Commandoschip": Commandoschip
        }

        g = self.game
        game_row, ships, asteroids = SaveManager.load_game(game_id)

        g.width = game_row["board_width"]
        g.length = game_row["board_length"]
        g.round_number = game_row["round_number"]
        g.current_player = game_row["current_player"]
        g.winner = game_row["winner"]

        g.player_exposed_cells = {
            tuple(map(int, k.split(","))): v
            for k, v in json.loads(game_row["player_exposed_cells"]).items()
        }
        g.enemy_exposed_cells = {
            tuple(map(int, k.split(","))): v
            for k, v in json.loads(game_row["enemy_exposed_cells"]).items()
        }

        g.actions = json.loads(game_row["actions"])

        g.player.ships = []
        g.enemy.ships = []
        for s in ships:
            ship = ship_classes[s["type"]]()
            ship.ShipPoint = (s["position_x"], s["position_y"])
            ship.orientation = orientation[s["orientation"]]
            ship.hit_cells = set(tuple(c) for c in json.loads(s["hit_cells"]))
            ship.SpcUseable = bool(s["spc_useable"])
            ship.emp_turns = s["emp_turns"]
            if s["owner"] == "player":
                g.player.ships.append(ship)
            else:
                g.enemy.ships.append(ship)

        g.player.asteroids = []
        g.enemy.asteroids = []
        for a in asteroids:
            asteroid_list = g.player.asteroids if a["owner"] == "player" else g.enemy.asteroids
            ship_list = g.player.ships if a["owner"] == "player" else g.enemy.ships
            asteroid_list.append(Asteroid(
                a["x"], a["y"],
                tuple(json.loads(a["direction"])),
                g, ship_list, asteroid_list
            ))

        g.phase = "play"
        print(f"Game {game_id} geladen")
        return True