from Game

class Lobby:
    def __init__(self, lobby_name):
        self.players = []
        self.lobby_name = lobby_name
        self.game = None

    def add_player(self, socket):
        self.players.append(socket)

    def start_game(self, game_type):
        if game_type == "game":


