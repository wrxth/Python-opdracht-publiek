import pygame
from Ships.Kruiser import Kruiser
from Ships.Jager import Jager
from Ships.Slagschip import Slagschip
from Ships.Verkenner import Verkenner
from Ships.Commandoschip import Commandoschip
from Ships.Orientation import orientation
from Move import Move
from Ui import Ui
from Asteroid import Asteroid
from datetime import datetime
from savemanager import SaveManager
from ClickHandler import ClickHandler
from GameLoader import GameLoader
from AIPlayer import AIPlayer

import random
import os, json
class Game:

    GameFieldSize = 500
    BoardXpos = 320
    BoardYpos = 50
    defaultOffset = 10
    defaultSpotSize = 50
    scalingSizeMod = 1.7

    selectorSquareSize = 50
    selectorSideOffset = 10
    selectorTopOffset = 100
    
    defaultSquareColor = (30,30,30)

    selectorspacing = 10
    def __init__(self, screen, font,width, length, player, enemy):
        self.width = width
        self.length = length
        self.font = font
        self.screen = screen
        self.clickedCells = []
        self.selectedShip = None
        self.Move = Move(self)
        self.Ui = Ui(self)
        self.ClickHandler = ClickHandler(self)
        self.GameLoader = GameLoader(self)
        self.player = player
        self.enemy = enemy
        self.show_enemy = False 
        self.cheat_mode = False
        self.GenerateEnemyShips()
        self.player_exposed_cells = {}
        self.enemy_exposed_cells = {}
        self.current_player = "player"
        self.turn_done = False
        self.round_number = 1
        self.phase = "setup" 
        self.game_mode = "Move"
        self.game_over = ""
        self.shipTypes = [Jager(), Kruiser(), Slagschip(), Verkenner(), Commandoschip()]
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.actions = []
        self.winner = None
        self.salvo_direction = "horizontal"
        self.active_special = None
        self.AI = AIPlayer(self)
    def CreateGameboard(self,width, length, xpos, ypos, ships, asteroid_list,exposed_cells,show_ships=True,show_asteroid_dir=False ):
            pygame.draw.rect(self.screen, (20,20,20), pygame.Rect((xpos, ypos, self.GameFieldSize, self.GameFieldSize)))
    
            xSpotSpacing = self.GameFieldSize / width
            ySpotSpacing = self.GameFieldSize / length

            spotHeight = self.defaultSpotSize - length * self.scalingSizeMod
            spotWidth = self.defaultSpotSize - width * self.scalingSizeMod

            occupied_cells = {(cx, cy): ship.color for ship in ships for cx, cy in ship}

            for xIndex in range(width):
                for yIndex in range(length):
                    xPos = xpos + self.defaultOffset + xSpotSpacing * xIndex
                    yPos = ypos + self.defaultOffset + ySpotSpacing * yIndex

                    rect = pygame.Rect((xPos, yPos, spotWidth, spotHeight))
                    color = self.defaultSquareColor  

                    if show_ships and (xIndex, yIndex) in occupied_cells:
                        color = occupied_cells[(xIndex, yIndex)]
                    pygame.draw.rect(self.screen, color, rect)

            for (cx,cy), status in exposed_cells.items():
                cell_x = xpos + self.defaultOffset + xSpotSpacing * cx
                cell_y = ypos + self.defaultOffset + ySpotSpacing * cy
                rect = pygame.Rect((cell_x, cell_y, spotWidth, spotHeight))
                
                ship_here = any((cx, cy) in ship for ship in ships)
               
                if ship_here and status == "miss":
                    pygame.draw.rect(self.screen, (200, 100, 0), rect)
                elif status == "miss":
                    pygame.draw.rect(self.screen, (80, 80, 80), rect)  
                elif status == "asteroid":
                    pygame.draw.rect(self.screen, (0, 200, 200), rect) 
                elif status == "scan_hit":
                    pygame.draw.rect(self.screen, (255, 200, 0), rect)   
                elif status == "scan_miss":
                    pygame.draw.rect(self.screen, (100, 100, 200), rect)
                elif status == "emp":
                    pygame.draw.rect(self.screen, (150, 0, 200), rect)    
                    
            for ship in ships:
                for cx, cy in ship.hit_cells:
                    if (cx, cy) in ship: 
                        cell_x = xpos + self.defaultOffset + xSpotSpacing * cx
                        cell_y = ypos + self.defaultOffset + ySpotSpacing * cy
                        rect = pygame.Rect((cell_x, cell_y, spotWidth, spotHeight))
                        pygame.draw.rect(self.screen, (200, 0, 0), rect)
            
            for asteroid in asteroid_list:
                ax = xpos + self.defaultOffset + xSpotSpacing * asteroid.x
                ay = ypos + self.defaultOffset + ySpotSpacing * asteroid.y
                rect = pygame.Rect((ax, ay, spotWidth, spotHeight))
                pygame.draw.rect(self.screen, (0, 200, 200), rect)
                if show_asteroid_dir:
                    self._DrawAsteroidDirection(asteroid, ax, ay, spotWidth, spotHeight)

    def CreateGame(self):
        if self.game_over:
            self.Ui.DrawEndScreen()
            return
        self.CreateGameboard(self.width, self.length, self.BoardXpos, self.BoardYpos, self.player.ships, self.player.asteroids,self.enemy_exposed_cells,show_ships=True,show_asteroid_dir=self.cheat_mode)
        enemy_xpos = self.BoardXpos + self.GameFieldSize + 100 
        self.CreateGameboard(self.width, self.length, enemy_xpos, self.BoardYpos, self.enemy.ships, self.enemy.asteroids,self.player_exposed_cells,show_ships=self.show_enemy,show_asteroid_dir=self.cheat_mode)
        self.CreateShipSelectors()
        self.Ui.DrawUI()

    def CreateShipSelectors(self):
        shipTypes = [Jager(), Kruiser(), Slagschip(), Verkenner(), Commandoschip()]
        self.selectorRects = []
        for index, ship in enumerate(shipTypes):
            ypos = self.selectorTopOffset + (self.selectorSquareSize + self.selectorspacing) * index
            rect = pygame.Rect((self.selectorSideOffset, ypos, self.selectorSquareSize, self.selectorSquareSize))
            self.selectorRects.append((rect,ship))

            pygame.draw.rect(self.screen, ship.color, rect)

            placed_of_type = sum(isinstance(s, ship.__class__) for s in self.player.ships)
            remaining = ship.count - placed_of_type
            textSurface = self.font.render(
                f"{ship.__class__.__name__} ({remaining} left)",
                True, (255, 255, 255)
            )
            textXpos = self.selectorSideOffset * 2 + self.selectorSquareSize
            textYpos = ypos + self.selectorSquareSize * .4

            self.screen.blit(textSurface,(textXpos,textYpos))

    def HandleShipPlacement(self, xIndex, yIndex):
        """Plaats een nieuw schip vanaf de selector."""
        if self.selectedShip is not None and not self.clickedCells:
            self.clickedCells.append((xIndex, yIndex))
        elif self.selectedShip is not None and self.clickedCells:
            dx = abs(self.clickedCells[0][0] - xIndex)
            dy = abs(self.clickedCells[0][1] - yIndex)
            if (dx < self.selectedShip.length and dy == 0) or (dy < self.selectedShip.length and dx == 0):
                nX = self.clickedCells[0][0] - xIndex
                nY = self.clickedCells[0][1] - yIndex

                if nX < 0:
                    self.selectedShip.orientation = orientation.Right
                elif nX > 0:
                    self.selectedShip.orientation = orientation.Left
                if nY > 0:
                    self.selectedShip.orientation = orientation.Up
                elif nY < 0:
                    self.selectedShip.orientation = orientation.Down

                self.selectedShip.ShipPoint = self.clickedCells[0][0], self.clickedCells[0][1]

                if not self.Move.check_collision(self.selectedShip):
                    self.player.ships.append(self.selectedShip)
                    print(f"{self.selectedShip.__class__.__name__} placed at {self.selectedShip.ShipPoint}")
            self.clickedCells.clear()
            
    
    def GenerateEnemyShips(self):
        shipTypes = [Jager(), Kruiser(), Slagschip(), Verkenner(), Commandoschip()]
        for template in shipTypes:
            for _ in range(template.count):
                ship = template.__class__()
                placed = False
                while not placed:
                    x = random.randint(0, self.width - 1)
                    y = random.randint(0, self.length - 1)
                    ship.ShipPoint = (x, y)
                    ship.orientation = random.choice(list(orientation))
                    if not self.Move.check_collision(ship, include_enemy=True):
                        self.enemy.ships.append(ship)
                        placed = True

    def Attack(self, targetX, targetY, exposed_cells,asteroid_list,enemy=True):
        if self.turn_done: 
            return "turn already used"

        board = self.enemy.ships if enemy else self.player.ships
        result = "miss"

        for ship in list(board):
            if (targetX,targetY) in ship:
                exposed_cells[(targetX,targetY)] = "hit"
                ship.hit_cells.add((targetX, targetY))
                result = "hit"

                if all(cell in ship.hit_cells for cell in ship):
                    print("ship destroyed")
                    board.remove(ship)
                    break

        if result == "miss":
            for asteroid in asteroid_list:
                if (asteroid.x,asteroid.y) == (targetX, targetY):
                    asteroid.change_direction_diagonal() 
                    exposed_cells[(targetX, targetY)] = "asteroid"
                    result = "asteroid"
                    break

        if result == "miss":
            exposed_cells[(targetX,targetY)] = "miss"

        self.turn_done = True
        return result

    def EndTurn(self):
        if self.current_player == "player":
            self.current_player = "ai"
            for ship in self.enemy.ships:
                if ship.emp_turns > 0:
                    ship.emp_turns -= 1
                    if ship.emp_turns == 0:
                        for cx, cy in ship:
                            if (cx, cy) in self.player_exposed_cells and self.player_exposed_cells[(cx, cy)] == "emp":
                                self.player_exposed_cells[(cx, cy)] = "hit"
        else:
            self.current_player = "player"
            self.round_number += 1
            self.move_asteroids()
        if not self.player.ships:
            self.game_over = "lose"
            self.winner = "AI"
            self.save_game()
        elif not self.enemy.ships:
            self.game_over = "win"
            self.winner = self.player.nickname 
            self.save_game()
    
        self.turn_done = False

    def spawn_asteroids(self, asteroid_list = [],n=4, ship_list = []):

        if asteroid_list is None:
            asteroid_list = []
        while len(asteroid_list) < n:
            x = random.randint(0, self.width - 1 )
            y = random.randint(0, self.length - 1 )

            valid = True
            for ship in ship_list:
                for cx,cy in ship:
                    if abs(cx - x) <= 1 and abs(cy - y) <= 1:
                        valid = False
                        break
                if not valid:
                    break
            
            if valid:
                asteroid_list.append(Asteroid(x,y,Asteroid.random_direction(),self,ship_list,asteroid_list))
    
    def move_asteroids(self):
        for asteroid in list(self.player.asteroids):
            asteroid.move()
        for asteroid in list(self.enemy.asteroids):
            asteroid.move()

    def save_game(self):
        self.GameLoader.save()

    def load_game(self, game_id):
        return self.GameLoader.load(game_id)
    
    def _DrawAsteroidDirection(self, asteroid, ax, ay, spotWidth, spotHeight):
        directions = {
            (1, 1):   (1, 1),
            (-1, 1):  (-1, 1),
            (1, -1):  (1, -1),
            (-1, -1): (-1, -1)
        }
        dx, dy = directions.get(asteroid.direction, (0, 0))
        
        center_x = int(ax + spotWidth // 2)
        center_y = int(ay + spotHeight // 2)
        end_x = int(center_x + dx * spotWidth // 3)
        end_y = int(center_y + dy * spotHeight // 3)
        
        pygame.draw.line(self.screen, (255, 255, 0), (center_x, center_y), (end_x, end_y), 2)
        pygame.draw.circle(self.screen, (255, 255, 0), (end_x, end_y), 3)