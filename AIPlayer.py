import random
from Ships.Orientation import orientation

class AIPlayer:
    def __init__(self, game):
        self.game = game

    def AITurn(self):
        g = self.game
        if g.turn_done:
            return
        
        action = random.choice(["attack", "move"])

        if action == "move" and g.enemy.ships:
            self._AIMoveShip()
        else:
            self._AIAttack()

    def _AIAttack(self):
        g = self.game
        tx = random.randint(0, g.width - 1)
        ty = random.randint(0, g.length - 1)
        print(f"AI attacks {tx},{ty}")
        g.Attack(tx, ty, g.enemy_exposed_cells, g.player.asteroids, enemy=False)
        g.actions.append({
            "player": "ai",
            "type": "attack",
            "target": (tx, ty),
            "round": g.round_number
        })
        g.turn_done = True

    def _AIMoveShip(self):
        g = self.game
        ship = random.choice(g.enemy.ships)
        
        if ship.is_emp:
            self._AIAttack()
            return

        if ship.orientation in (orientation.Right, orientation.Left):
            directions = [(1, 0), (-1, 0)]
        else:
            directions = [(0, 1), (0, -1)]

        random.shuffle(directions)
        sx, sy = ship.ShipPoint

        for dx, dy in directions:
            new_dir = (sx + dx, sy + dy)
            old_point = ship.ShipPoint
            ship.ShipPoint = new_dir

            if not g.Move.check_collision(ship, ignore_ship=ship, include_enemy=True):
                dx_moved = new_dir[0] - old_point[0]
                dy_moved = new_dir[1] - old_point[1]
                ship.hit_cells = {(hx + dx_moved, hy + dy_moved) for hx, hy in ship.hit_cells}
                g.actions.append({
                    "player": "ai",
                    "type": "move",
                    "ship": ship.__class__.__name__,
                    "round": g.round_number
                })
                g.turn_done = True
                return
            else:
                ship.ShipPoint = old_point

        self._AIAttack()