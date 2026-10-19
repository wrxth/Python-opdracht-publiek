from Ships.Orientation import orientation

class ClickHandler:
    def __init__(self, game):
        self.game = game

    def HandleClick(self, mouse_pos):
        g = self.game
        if g.game_over:
            if hasattr(g, "end_menu_button") and g.end_menu_button.collidepoint(mouse_pos):
                return "goto_menu"
            return
        
        mx, my = mouse_pos
        xSpotSpacing = g.GameFieldSize / g.width
        ySpotSpacing = g.GameFieldSize / g.length

        if g.phase == "setup":
            self._HandleSetupClick(mx, my, xSpotSpacing, ySpotSpacing)
        elif g.phase == "play":
            self._HandlePlayClick(mx, my, xSpotSpacing, ySpotSpacing)
        elif g.phase == "menu":
            self._HandleMenuClick(mx, my)

    def _HandleSetupClick(self, mx, my, xSpotSpacing, ySpotSpacing):
        g = self.game
        for rect, ship in g.selectorRects:
            if rect.collidepoint(mx, my):
                placed_of_type = sum(isinstance(s, ship.__class__) for s in g.player.ships)
                if placed_of_type < ship.count:
                    print(f"Selected ship to place: {ship.__class__.__name__}")
                    g.selectedShip = ship.__class__()
                else:
                    print(f"Max {ship.count}x {ship.__class__.__name__} already placed!")
                return

        if (g.BoardXpos <= mx <= g.BoardXpos + g.GameFieldSize and
                g.BoardYpos <= my <= g.BoardYpos + g.GameFieldSize):

            xIndex = int((mx - g.BoardXpos) / xSpotSpacing)
            yIndex = int((my - g.BoardYpos) / ySpotSpacing)

            if g.selectedShip is not None and not g.clickedCells:
                g.clickedCells.append((xIndex, yIndex))

            elif g.selectedShip is not None and g.clickedCells:
                startX, startY = g.clickedCells[0]
                dx = xIndex - startX
                dy = yIndex - startY

                if abs(dx) < g.selectedShip.length and dy == 0:
                    g.selectedShip.orientation = orientation.Right if dx > 0 else orientation.Left
                elif abs(dy) < g.selectedShip.length and dx == 0:
                    g.selectedShip.orientation = orientation.Down if dy > 0 else orientation.Up
                else:
                    print("Invalid placement")
                    g.clickedCells.clear()
                    return

                g.selectedShip.ShipPoint = (startX, startY)

                if not g.Move.check_collision(g.selectedShip):
                    g.player.ships.append(g.selectedShip)
                    print(f"Placed {g.selectedShip.__class__.__name__} at {startX},{startY}")
                else:
                    print("Placement collision detected!")

                g.clickedCells.clear()
                g.selectedShip = None

                total_required = sum(s.count for s in g.shipTypes)
                if len(g.player.ships) >= total_required:
                    print("All ships placed! Game starts...")
                    g.phase = "play"
                    g.game_mode = "attack"
                    g.spawn_asteroids(g.player.asteroids, 4, g.player.ships)
                    g.spawn_asteroids(g.enemy.asteroids, 4, g.enemy.ships)
            else:
                g.clickedCells.clear()

    def _HandlePlayClick(self, mx, my, xSpotSpacing, ySpotSpacing):
        g = self.game
        for name, rect in g.Ui.ui_buttons.items():
            if rect.collidepoint(mx, my):
                if name == "special" and g.selectedShip is not None:
                    g.game_mode = "special"
                elif name == "salvo_dir":
                    g.salvo_direction = "vertical" if g.salvo_direction == "horizontal" else "horizontal"
                else:
                    g.game_mode = name
                return

        if g.game_mode == "move":
            self.HandleShipMove(mx, my, xSpotSpacing, ySpotSpacing)
        elif g.game_mode == "attack":
            self.HandleAttackClick(mx, my)
        elif g.game_mode == "special":
            self.HandleSpecialClick(mx, my)

    def _HandleMenuClick(self, mx, my):
        g = self.game
        for name, rect in g.Ui.ui_buttons.items():
            if rect.collidepoint(mx, my):
                if name == "load":
                    g.phase = "loadmenu"
                    g.load_available_saves()
                    return

    def HandleShipMove(self, mx, my, xSpotSpacing, ySpotSpacing):
        g = self.game
        if (g.BoardXpos <= mx <= g.BoardXpos + g.GameFieldSize and
                g.BoardYpos <= my <= g.BoardYpos + g.GameFieldSize):

            xIndex = int((mx - g.BoardXpos) / xSpotSpacing)
            yIndex = int((my - g.BoardYpos) / ySpotSpacing)

            if g.selectedShip is None:
                for ship in g.player.ships:
                    if (xIndex, yIndex) in ship:
                        print(f"Selected ship to move: {ship.__class__.__name__}")
                        g.selectedShip = ship
                        return
            else:
                g.Move.move(g.selectedShip, (xIndex, yIndex))
                g.selectedShip = None
                g.EndTurn()

    def HandleAttackClick(self, mx, my):
        g = self.game
        enemy_xpos = g.BoardXpos + g.GameFieldSize + 100
        xSpotSpacing = g.GameFieldSize / g.width
        ySpotSpacing = g.GameFieldSize / g.length

        if (enemy_xpos <= mx <= enemy_xpos + g.GameFieldSize and
                g.BoardYpos <= my <= g.BoardYpos + g.GameFieldSize):

            xIndex = int((mx - enemy_xpos) / xSpotSpacing)
            yIndex = int((my - g.BoardYpos) / ySpotSpacing)

            result = g.Attack(xIndex, yIndex, g.player_exposed_cells, g.enemy.asteroids, enemy=True)
            g.actions.append({
                "player": "human",
                "type": "attack",
                "target": (xIndex, yIndex),
                "result": result,
                "round": g.round_number
            })
            if result in ["hit", "miss", "asteroid"]:
                g.EndTurn()

    def HandleSpecialClick(self, mx, my):
        g = self.game
        enemy_xpos = g.BoardXpos + g.GameFieldSize + 100
        xSpotSpacing = g.GameFieldSize / g.width
        ySpotSpacing = g.GameFieldSize / g.length

        if g.active_special is None and g.selectedShip is not None:
            g.active_special = g.selectedShip

        if g.active_special is None:
            if (g.BoardXpos <= mx <= g.BoardXpos + g.GameFieldSize and
                    g.BoardYpos <= my <= g.BoardYpos + g.GameFieldSize):
                xIndex = int((mx - g.BoardXpos) / xSpotSpacing)
                yIndex = int((my - g.BoardYpos) / ySpotSpacing)
                for ship in g.player.ships:
                    if (xIndex, yIndex) in ship:
                        if not getattr(ship, "SpcUseable", True):
                            print(f"{ship.__class__.__name__} special al gebruikt")
                            return
                        g.active_special = ship
                        g.selectedShip = ship
                        return
            return

        if (enemy_xpos <= mx <= enemy_xpos + g.GameFieldSize and
                g.BoardYpos <= my <= g.BoardYpos + g.GameFieldSize):
            xIndex = int((mx - enemy_xpos) / xSpotSpacing)
            yIndex = int((my - g.BoardYpos) / ySpotSpacing)
            board = "enemy"
        elif (g.BoardXpos <= mx <= g.BoardXpos + g.GameFieldSize and
                g.BoardYpos <= my <= g.BoardYpos + g.GameFieldSize):
            xIndex = int((mx - g.BoardXpos) / xSpotSpacing)
            yIndex = int((my - g.BoardYpos) / ySpotSpacing)
            board = "player"
        else:
            return

        g.active_special.specialAtk(xIndex, yIndex, board, g)
        g.active_special = None
        g.selectedShip = None
        g.game_mode = "attack"
        g.EndTurn()