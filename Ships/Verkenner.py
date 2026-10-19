from Ships.BaseShip import BaseShip
from OncePerGameShipDeco import OnceDeco
from Ships.Orientation import orientation


class Verkenner(BaseShip):
    

    @property
    def length(self):
        
        return 2

    @property
    def count(self):
        "base class count"
        return 2
    
    @property
    def color(self):
        "base class color"
        return (255,0,255)
    
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
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                cx, cy = x + dx, y + dy
                if 0 <= cx < game.width and 0 <= cy < game.length:
                    ships = game.enemy.ships if board == "enemy" else game.player.ships
                    hit = any((cx, cy) in ship for ship in ships)
                    status = "scan_hit" if hit else "scan_miss"
                    game.player_exposed_cells[(cx, cy)] = status