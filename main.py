import threading
import random
import string

from queue import Queue

from host import Host
from game import Game

def start_server(code: str, join_q: Queue, disc_q: Queue, draw_q: Queue, vote_q: Queue, msg_q: Queue):
    host = Host(code, join_q, disc_q, draw_q, vote_q, msg_q)
    host.run()

def start_game(code: str, join_q: Queue, disc_q: Queue, draw_q: Queue, vote_q: Queue, msg_q: Queue):
    game = Game(code, join_q, disc_q, draw_q, vote_q, msg_q)
    game.game_loop()

if __name__ == "__main__":
    code = ''.join(random.choices(string.ascii_uppercase, k=4))
    join_q = Queue()
    disc_q = Queue()
    draw_q = Queue()
    vote_q = Queue()
    msg_q = Queue()
    shared_args = [code, join_q, disc_q, draw_q, vote_q, msg_q]

    # The server runs in a daemon thread so it dies with the program.
    server_thread = threading.Thread(target=start_server, args=shared_args, daemon=True)
    server_thread.start()

    # pygame runs on the main thread (required on macOS, safer everywhere).
    # Closing the window ends game_loop -> sys.exit(), which now ends the whole program.
    start_game(*shared_args)