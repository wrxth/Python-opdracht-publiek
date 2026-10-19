from Ships.BaseShip import BaseShip
from OncePerGameShipDeco import OnceDeco
from Ships.Orientation import orientation


class Jager(BaseShip):

    @property
    def length(self):
        
        return 3

    @property
    def count(self):
        "base class count"
        return 2
    
    @property
    def color(self):
        "base class color"
        return (255,0,0)
    
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
        enemy_ships = game.enemy.ships

        if not enemy_ships:
            return
        
        
        clossest_cell = min(
            ((cx, cy, ship) for ship in enemy_ships for cx, cy in ship),
            key=lambda c:abs(c[0] - x) + abs(c[1] - y)
        )

        cx, cy, ship = clossest_cell
        game.player_exposed_cells[(cx,cy)] = "hit"
        ship.hit_cells.add((cx, cy))


        ship = next(s for s in enemy_ships if (cx, cy) in s)
        if all(cell in game.player_exposed_cells for cell in ship):
            game.enemy.ships.remove(ship)