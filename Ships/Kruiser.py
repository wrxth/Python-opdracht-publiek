from Ships.BaseShip import BaseShip
from OncePerGameShipDeco import OnceDeco
from Ships.Orientation import orientation


class Kruiser(BaseShip):
    
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
        return (0,255,0)
    
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
        target_ship = next(
            (s for s in game.enemy.ships if (x, y) in s
            and (x, y) in game.player_exposed_cells),
            None
        )
        
        if target_ship is None:
            print("Geen zichtbaar vijandelijk schip op die cel")
            self.SpcUseable = True  
            return

        target_ship.emp_turns = 4
        print(f"{target_ship.__class__.__name__} is uitgeschakeld voor 3 beurten")
        for cx, cy in target_ship:
            if (cx, cy) in game.player_exposed_cells:
                game.player_exposed_cells[(cx, cy)] = "emp"