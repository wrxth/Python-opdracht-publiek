import pygame
class Ui:
    def __init__(self,game):
        self.game =  game
        self.ui_buttons = {
        "move": pygame.Rect(20, 600, 100, 40),
        "attack": pygame.Rect(140, 600, 100, 40),
        "special": pygame.Rect(260, 600, 100, 40),
        "salvo_dir": pygame.Rect(380, 600, 140, 40)
        }

    def DrawUI(self):
        """Tekent HUD met fase, mode, geselecteerd schip en speler info"""
        y = 700 
        line_height = 25
        white = (255, 255, 255)

    # Fase
        phase_text = f"Phase: {self.game.phase}"
        phase_surface = self.game.font.render(phase_text, True, white)
        self.game.screen.blit(phase_surface, (self.game.BoardXpos, y))
        y += line_height

    # Speler aan de beurt
        turn_text = f"Current Player: {self.game.player.nickname}"
        turn_surface = self.game.font.render(turn_text, True, white)
        self.game.screen.blit(turn_surface, (self.game.BoardXpos, y))
        y += line_height

        round_text = f"Round: {self.game.round_number}"
        round_surface = self.game.font.render(round_text, True, white)
        self.game.screen.blit(round_surface, (self.game.BoardXpos, y))
        y += line_height

    # Game mode (attack/move)
        if self.game.phase == "play":
            mode_text = f"Mode: {self.game.game_mode}"
            mode_surface = self.game.font.render(mode_text, True, white)
            self.game.screen.blit(mode_surface, (self.game.BoardXpos, y))
            y += line_height

        if (hasattr(self.game, "selectedShip") and 
            self.game.selectedShip.__class__.__name__ == "Slagschip" and
            self.game.game_mode == "special"):
            rect = self.ui_buttons["salvo_dir"]
            pygame.draw.rect(self.game.screen, (80, 80, 80), rect)
            label = f"Richting: {self.game.salvo_direction}"
            text = self.game.font.render(label, True, (255, 255, 255))
            self.game.screen.blit(text, (rect.x + 50, rect.y + 10))
        

    # Geselecteerd schip
        if hasattr(self.game, "selectedShip") and self.game.selectedShip is not None:
            sel_text = f"Selected Ship: {self.game.selectedShip.__class__.__name__}"
            sel_surface = self.game.font.render(sel_text, True, white)
            self.game.screen.blit(sel_surface, (self.game.BoardXpos, y))
            y += line_height

        for name, rect in self.ui_buttons.items():
            color = (0,200,0) if self.game.game_mode == name else (80,80,80)
            pygame.draw.rect(self.game.screen, color, rect)

            text = self.game.font.render(name.capitalize(), True, (255,255,255))
            text_x = rect.x + (rect.width - text.get_width()) // 2
            text_y = rect.y + (rect.height - text.get_height()) // 2
            self.game.screen.blit(text, (text_x, text_y))

    def DrawEndScreen(self):
        self.game.screen.fill((20, 20, 20))

        self.game.CreateGameboard(self.game.width, self.game.length, self.game.BoardXpos, self.game.BoardYpos,
                            self.game.player.ships, self.game.player.asteroids, self.game.enemy_exposed_cells, show_ships=True)
        enemy_xpos = self.game.BoardXpos + self.game.GameFieldSize + 100
        self.game.CreateGameboard(self.game.width, self.game.length, enemy_xpos, self.game.BoardYpos,
                            self.game.enemy.ships, self.game.enemy.asteroids, self.game.player_exposed_cells, show_ships=True)

        player_label = self.game.font.render(f"{self.game.player.nickname}", True, (255, 255, 255))
        enemy_label = self.game.font.render("Computer", True, (255, 255, 255))
        self.game.screen.blit(player_label, (self.game.BoardXpos, self.game.BoardYpos - 30))
        self.game.screen.blit(enemy_label, (enemy_xpos, self.game.BoardYpos - 30))

        color = (0, 255, 0) if self.game.game_over == "win" else (255, 0, 0)
        text = "YOU WIN!" if self.game.game_over == "win" else "YOU LOSE!"
        font_big = pygame.font.SysFont("Arial", 64, bold=True)
        winner_surface = font_big.render(text, True, color)
        self.game.screen.blit(winner_surface, (
            self.game.screen.get_width() // 2 - winner_surface.get_width() // 2,
            self.game.BoardYpos + self.game.GameFieldSize + 20
        ))

        name_surface = self.game.font.render(f"Winnaar: {self.game.winner}", True, (255, 255, 255))
        self.game.screen.blit(name_surface, (
            self.game.screen.get_width() // 2 - name_surface.get_width() // 2,
            self.game.BoardYpos + self.game.GameFieldSize + 90
        ))

        self.game.end_menu_button = pygame.Rect(
            self.game.screen.get_width() // 2 - 100,
            self.game.BoardYpos + self.game.GameFieldSize + 130,
            200, 50
        )
        pygame.draw.rect(self.game.screen, (0, 150, 0), self.game.end_menu_button, border_radius=8)
        btn_text = self.game.font.render("Terug naar menu", True, (255, 255, 255))
        self.game.screen.blit(btn_text, (
            self.game.end_menu_button.x + self.game.end_menu_button.width // 2 - btn_text.get_width() // 2,
            self.game.end_menu_button.y + 15
        ))
    
    def DrawLoadMenu(self):
        self.ui_buttons = {}
        y = 100
        for i, save in enumerate(self.game.available_saves):
            rect = pygame.Rect(700, y, 200, 40)
            pygame.draw.rect(self.game.screen, (50, 150, 50), rect)
            text = self.font.render(save, True, (255,255,255))
            self.game.screen.blit(text, (710, y+10))
            self.ui_buttons[f"save_{i}"] = rect
            y += 50

    def draw_button(screen, text, rect, font, active=True):
        color = (0, 200, 0) if active else (150, 150, 150)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        txt = font.render(text, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=rect.center)
        screen.blit(txt, txt_rect)