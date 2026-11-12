import threading
import socket
import os
import sys
import random
import string

from queue import Queue

from host import Host
from game import Game

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)


def get_local_ip() -> str:
    '''best guess at this PC's LAN address (the one other devices on the network should type in)'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # UDP "connect" only picks a route, no packets are sent
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()

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

    print("\n==============================")
    print(f" Box code:        {code}")
    print(f" Server address:  {get_local_ip()}")
    print("==============================")

    # The server runs in a daemon thread so it dies with the program.
    server_thread = threading.Thread(target=start_server, args=shared_args, daemon=True)
    server_thread.start()

    # pygame runs on the main thread (required on macOS, safer everywhere).
    # Closing the window ends game_loop -> sys.exit(), which now ends the whole program.
    start_game(*shared_args)