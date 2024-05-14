import threading
import random
import string

from queue import Queue

from host import Host
from game import Game

def start_server(code: str, msg_queue: Queue):
    host = Host(code, msg_queue)
    host.run()

def start_game(code: str, msg_queue: Queue):
    game = Game(code, msg_queue)
    game.game_loop()

if __name__ == "__main__":
    code = ''.join(random.choices(string.ascii_uppercase, k=4))
    msg_queue = Queue()
    shared_args = [code, msg_queue]
    server_thread = threading.Thread(target=start_server, args=shared_args)
    game_thread = threading.Thread(target=start_game, args=shared_args)

    server_thread.start()
    game_thread.start()

    server_thread.join()
    game_thread.join()