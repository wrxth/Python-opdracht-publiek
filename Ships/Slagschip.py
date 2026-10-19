from Ships.BaseShip import BaseShip
from OncePerGameShipDeco import OnceDeco
from Ships.Orientation import orientation


class Slagschip(BaseShip):
    
    @property
    def length(self):
        
        return 4

    @property
    def count(self):
        "base class count"
        return 1
    
    @property
    def color(self):
        "base class color"
        return (0,0,255)
    
    @property
    def orientation(self) -> orientation:

        return self._orientation
    
    @orientation.setter
    def orientation(self, value: orientation):
        if not isinstance(value,orientation):
            raise ValueError("incorrect data ingestuurd")
        
        self._orientation = value

    @property
    def ShipPoint(self):
        return self._ShipPoint

    @ShipPoint.setter
    def ShipPoint(self, value):
        self._ShipPoint = value

    @OnceDeco
    def specialAtk(self, x, y, board, game):
        cells = []
        for i in range(3):
            if game.salvo_direction == "horizontal":
                cells.append((x + i, y))
            else:
                cells.append((x, y + i))

        for cx, cy in cells:
            if not (0 <= cx < game.width and 0 <= cy < game.length):
                continue

            hit = any((cx, cy) in ship for ship in game.enemy.ships)
            game.player_exposed_cells[(cx, cy)] = "hit" if hit else "miss"

            if hit:
                ship = next(s for s in game.enemy.ships if (cx, cy) in s)
                ship.hit_cells.add((cx, cy))
                if all(cell in game.player_exposed_cells for cell in ship):
                    game.enemy.ships.remove(ship)