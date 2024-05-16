import threading
import random
import string

from queue import Queue

from host import Host
from game import Game
from models import DrawingData

def start_server(code: str, join_q: Queue, disc_q: Queue):
    host = Host(code, join_q, disc_q)
    host.run()

def start_game(code: str, join_q: Queue, disc_q: Queue):
    game = Game(code, join_q, disc_q)
    game.game_loop()

if __name__ == "__main__":
    code = ''.join(random.choices(string.ascii_uppercase, k=4))
    join_q = Queue()
    disc_q = Queue()
    draw_q = Queue()
    shared_args = [code, join_q, disc_q, draw_q]
    server_thread = threading.Thread(target=start_server, args=shared_args)
    game_thread = threading.Thread(target=start_game, args=shared_args)

    server_thread.start()
    game_thread.start()

    server_thread.join()
    game_thread.join()