from game import Game

class Host:
    def __init__(self):
        pass

if __name__ == "__main__":
    game = Game()
    game.game_loop()
    game.add_player("chungus")