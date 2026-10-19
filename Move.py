from Ships.BaseShip import BaseShip
from Ships.Orientation import orientation
class Move:

    def __init__(self,game):
        self.game = game
    def move(self,ship,NewDir):
        if ship.is_emp:
            print(f"{ship.__class__.__name__} kan niet bewegen (EMP)")
            return
        
        cx, cy = NewDir
        oldCx, oldCy = ship.ShipPoint
        newCx, newCy = (oldCx,oldCy)

        if ship.orientation in (orientation.Right, orientation.Left):
            if cx > oldCx:
                newCx += 1
            elif cx < oldCx:
                newCx -= 1
        
        if ship.orientation in (orientation.Up, orientation.Down):
            if cy > oldCy:
                newCy += 1
            elif cy < oldCy:
                newCy -= 1
        NewPos = (newCx,newCy)
        ship.ShipPoint = NewPos
        print(f"new pos: {NewPos} shippoint: {ship.ShipPoint}")

        for asteroid in list(self.game.player.asteroids):
            if asteroid.check_ship_collision(newCx, newCy):
                return


        if  self.check_collision(ship,ship):
            ship.ShipPoint = (oldCx,oldCy)
            print("collisie is geraakt")
            
        dx = newCx - oldCx
        dy = newCy - oldCy
        ship.hit_cells = {(hx + dx, hy + dy) for hx, hy in ship.hit_cells}
        


    
    def check_collision(self,ship, ignore_ship=None, include_enemy=False):

        for cx,cy in ship:
            if not (0<= cx < self.game.width and 0 <= cy < self.game.length):
                return True
            
            for other in self.game.player.ships:
                if other is ignore_ship:
                    continue
                if (cx, cy) in other:
                    return True
            
            if include_enemy:
                for other in self.game.enemy.ships:
                    if other is ignore_ship:
                        continue
                    if (cx, cy) in other:
                        return True

        return False
