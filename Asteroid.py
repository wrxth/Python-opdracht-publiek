import random
class Asteroid:
    def __init__(self,x,y,direction,game,ships,asteroid_list):
        self.x = x
        self.y = y
        self.direction = direction
        self.game = game
        self.ships = ships
        self.asteroid_list = asteroid_list

    def __str__(self):
        return f"Asteroid at ({self.x},{self.y}) dir={self.direction}"
    
    def random_direction():
        return random.choice([(1,1), (-1,1), (1,-1), (-1,-1)])
    
    def check_ship_collision(self, x, y):
        for ship in self.ships:
            if (x, y) in ship:
                ship.hit_cells.add((x, y))
                if all(cell in ship.hit_cells for cell in ship):
                    self.ships.remove(ship)
                    print(f"{ship.__class__.__name__} vernietigd door asteroïde")
                self.asteroid_list.remove(self)
                return True
        return False
    
    def move(self):
        dx, dy = self.direction
        new_x = (self.x + dx) % self.game.width
        new_y = (self.y + dy) % self.game.length

        if self.check_ship_collision(new_x, new_y):
            return
            
        for other in list(self.asteroid_list):
            if other is not self and (new_x, new_y) == (other.x, other.y):
                if self in self.asteroid_list:
                    self.asteroid_list.remove(other)
                if self in self.asteroid_list:
                    self.asteroid_list.remove(self)
                self.game.spawn_asteroids(self.asteroid_list, 4, self.ships)
                return
            
        self.x, self.y = new_x, new_y

    def change_direction_diagonal(self):
        if self.direction == ((1,1)):
            self.direction = ((-1,-1))
        elif self.direction == ((-1,-1)):
            self.direction = ((1,1))
        elif self.direction == ((-1,1)):
            self.direction = ((1,-1))
        elif self.direction == ((1,-1)):
            self.direction = ((-1,1))
        