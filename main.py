import pygame
from Player import Player
from Game import Game
from Ui import Ui
from savemanager import SaveManager


pygame.init()

ScreenWidth = 1920
ScreenHeight = 1080

screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))
pygame.display.set_caption("test turn")

font = pygame.font.Font(None, 32)

state = "menu"
load_button = pygame.Rect(ScreenWidth - 220, 100, 200, 50)


available_saves = []

def draw_saves_menu(screen, font, saves):
    screen.fill((50, 50, 50))
    title = font.render("Opgeslagen spellen", True, (255, 255, 255))
    screen.blit(title, (ScreenWidth // 2 - title.get_width() // 2, 40))

    back_rect = pygame.Rect(20, 20, 100, 40)
    draw_button(screen, "Terug", back_rect, font)

    save_rects = []
    for i, save in enumerate(saves):
        y = 120 + i * 70
        
        # Info label
        info_rect = pygame.Rect(ScreenWidth // 2 - 300, y, 400, 50)
        pygame.draw.rect(screen, (70, 70, 70), info_rect, border_radius=8)
        winner = save['winner'] if save['winner'] else 'onbekend'
        label = f"{save['player_name']}  |  {save['start_time']}  |  {save['board_width']}x{save['board_length']}  |  {winner}"
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, (info_rect.x + 10, info_rect.y + 15))

        # Laden knop
        load_rect = pygame.Rect(ScreenWidth // 2 + 250, y, 80, 50)
        draw_button(screen, "Laden", load_rect, font)

        # Statistieken knop
        stats_rect = pygame.Rect(ScreenWidth // 2 + 340, y, 110, 50)
        draw_button(screen, "Bekijken", stats_rect, font)

        save_rects.append((load_rect, stats_rect, save["id"]))

    return back_rect, save_rects

def draw_button(screen, text, rect, font, active=True):
    color = (0, 200, 0) if active else (150, 150, 150)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    txt = font.render(text, True, (255, 255, 255))
    txt_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, txt_rect)

def get_input(screen, font, prompt_text, numeric_only=False):
    user_input = ""
    input_active = True

    while input_active:
        screen.fill((50, 50, 50))

        # Render prompt
        prompt = font.render(prompt_text, True, (255, 255, 255))
        screen.blit(prompt, (ScreenWidth // 2 - prompt.get_width() // 2, 300))

        # Render typed text
        text_surface = font.render(user_input, True, (200, 200, 0))
        screen.blit(text_surface, (ScreenWidth // 2 - text_surface.get_width() // 2, 400))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and user_input.strip() != "":
                    return user_input
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    if numeric_only:
                        if event.unicode.isdigit():
                            user_input += event.unicode
                    else:
                        user_input += event.unicode

def draw_stats_screen(screen, font, game):
    screen.fill((20, 20, 20))

    # Titel
    title = font.render("Spelstatistieken", True, (255, 255, 255))
    screen.blit(title, (ScreenWidth // 2 - title.get_width() // 2, 20))

    # Stats
    stats = [
        f"Speler: {game.player.nickname}",
        f"Gestart: {game.start_time}",
        f"Bordgrootte: {game.width}x{game.length}",
        f"Rondes gespeeld: {game.round_number}",
        f"Winnaar: {game.winner if game.winner else 'Nog bezig'}",
        f"Acties uitgevoerd: {len(game.actions)}"
    ]

    y = 600
    for stat in stats:
        text = font.render(stat, True, (200, 200, 200))
        screen.blit(text, (ScreenWidth // 2 - text.get_width() // 2, y))
        y += 30

    # Beide borden
    game.CreateGameboard(game.width, game.length, game.BoardXpos, game.BoardYpos,
                        game.player.ships, game.player.asteroids,
                        game.enemy_exposed_cells, show_ships=True)
    enemy_xpos = game.BoardXpos + game.GameFieldSize + 100
    game.CreateGameboard(game.width, game.length, enemy_xpos, game.BoardYpos,
                        game.enemy.ships, game.enemy.asteroids,
                        game.player_exposed_cells, show_ships=True)

    # Labels
    player_label = font.render(game.player.nickname, True, (255, 255, 255))
    enemy_label = font.render("Computer", True, (255, 255, 255))
    screen.blit(player_label, (game.BoardXpos, game.BoardYpos - 25))
    screen.blit(enemy_label, (enemy_xpos, game.BoardYpos - 25))

    # Terug knop
    back_rect = pygame.Rect(ScreenWidth // 2 - 100, ScreenHeight - 80, 200, 50)
    draw_button(screen, "Terug", back_rect, font)
    return back_rect

def get_board_size(screen, font):
    while True:
        size_input = get_input(screen, font, "Enter board size (8-16):", numeric_only=True)
        if size_input.strip() == "":
            continue
        size = int(size_input)
        if 8 <= size <= 16:
            return size
        # Toon foutmelding
        screen.fill((50, 50, 50))
        error = font.render("Board size must be between 8 and 16!", True, (255, 0, 0))
        screen.blit(error, (ScreenWidth // 2 - error.get_width() // 2, 350))
        pygame.display.update()
        pygame.time.wait(1500)

# --- MAIN LOOP ---
game = None
player = None
enemy = None
run = True
back_rect = None
save_rects = []
stats_back_rect = None

while run:
    screen.fill((100,100,100))

    if state == "menu":
        draw_button(screen, "New Game", pygame.Rect(100, 100, 200, 50), font)
        draw_button(screen, "Load Game", load_button, font, active=True)
    
    elif state == "saves":
        back_rect, save_rects = draw_saves_menu(screen, font, available_saves)
    elif state == "stats":
        stats_back_rect = draw_stats_screen(screen, font, game)

    elif state == "playing":
        game.CreateGame()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.save_game()
            run = False
        elif event.type == pygame.KEYDOWN:
            if game and state == "playing":
                if event.key == pygame.K_F1:  # cheat: instant win
                    game.enemy.ships.clear()
                    game.game_over = "win"
                    game.winner = game.player.nickname
                    game.save_game()
                elif event.key == pygame.K_F2:  # cheat: show enemies & dirs
                    game.cheat_mode = not game.cheat_mode
                    game.show_enemy = game.cheat_mode
                    print(f"Cheat mode: {game.cheat_mode}")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if state == "menu":
                if pygame.Rect(100, 100, 200, 50).collidepoint(pos):
                    nickname = get_input(screen, font, "Enter your nickname:")
                    board_size = get_board_size(screen, font)

                    player = Player(nickname, is_ai=False)
                    enemy = Player("Computer", is_ai=True)
                    game = Game(screen, font, board_size, board_size, player, enemy)
                    state = "playing"
                elif load_button.collidepoint(pos):
                    available_saves = SaveManager.load_saves()
                    state = "saves"

                
            elif state == "saves":
                if back_rect and back_rect.collidepoint(pos):
                    state = "menu"

                for load_rect, stats_rect, game_id in save_rects:
                    if load_rect.collidepoint(pos):
                        dummy_player = Player("temp", is_ai=False)
                        dummy_enemy = Player("Computer", is_ai=True)
                        game = Game(screen, font, 16, 16, dummy_player, dummy_enemy)
                        if game.load_game(game_id):
                            state = "playing"
                        break

                    if stats_rect.collidepoint(pos):
                        dummy_player = Player("temp", is_ai=False)
                        dummy_enemy = Player("Computer", is_ai=True)
                        game = Game(screen, font, 16, 16, dummy_player, dummy_enemy)
                        if game.load_game(game_id):
                            state = "stats"
                        break

            elif state == "stats":
                if stats_back_rect and stats_back_rect.collidepoint(pos):
                    state = "saves"

            elif state == "playing":
                result = game.ClickHandler.HandleClick(pos)
                if result == "goto_menu":
                    state = "menu"
                    game = None


    if state == "playing":
        if game.current_player == "ai" and not game.turn_done:
            game.AI.AITurn()
            game.EndTurn()

    pygame.display.update()

pygame.quit()
