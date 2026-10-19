from Ships.BaseShip import BaseShip
from OncePerGameShipDeco import OnceDeco
from Ships.Orientation import orientation

class Commandoschip(BaseShip):

    @property
    def length(self):
        
        return 5

    @property
    def count(self):
        "base class count"
        return 1
    
    @property
    def color(self):
        "base class color"
        return (255,255,255)

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
        print(f"Space Smoke op ({x}, {y}), board={board}")
        print("commando ship hoort iets te doen")

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                cx, cy = x + dx, y + dy
                if (cx, cy) in game.enemy_exposed_cells:
                    del game.enemy_exposed_cells[(cx, cy)]
                    print(f"Trying to remove ({cx}, {cy}), exists: {(cx, cy) in game.enemy_exposed_cells}")
