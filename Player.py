class Player:
    def __init__(self, nickname, is_ai=False):
        self.nickname = nickname
        self.is_ai = is_ai
        self.ships = []
        self.asteroids = []

    def __str__(self):
        return f"Player({self.nickname}, AI={self.is_ai})"