import threading

from host import Host
from game import Game

def start_server():
    host = Host()
    host.run()

def start_game():
    game = Game()
    game.game_loop()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    game_thread = threading.Thread(target=start_game)

    server_thread.start()
    game_thread.start()

    server_thread.join()
    game_thread.join()