# from game import Game
# from player import Player
import socket
import sys
import eventlet
import socketio
import random
import string

class Host:
    def __init__(self):
        self.sio = socketio.Server(cors_allowed_origins="*")
        self.app = socketio.WSGIApp(self.sio)
        self.players = dict()
        self.gameCode = ''.join(random.choices(string.ascii_uppercase, k=4))
        print(f"\nBox code: {self.gameCode}\n")

        # init events
        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.on("gameCode", self.checkCode)
        self.sio.on("userName", self.newUser)

    def run(self):
        '''start the server'''
        eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5100)), self.app, log_output=False)

    def printServerInfo(self):
        print(f"\nBox code: {self.gameCode}\n")
        print(f"Players: {list(self.players.values())}")

    def connect(self, sid, environ):
        print(f"New client {sid} connected.")
        self.players[sid] = f"Player {len(self.players) + 1}"
        self.printServerInfo()

    def disconnect(self, sid):
        print(f"Client {sid} ({self.players[sid]}) disconnected.")
        del self.players[sid]
        self.printServerInfo()

    def checkCode(self, sid, data):
        print(f"Received game code {data} from connected client {sid}.")
        if(data == self.gameCode):
            self.sio.emit("codeAccepted", room=sid)
            print(f"Client {sid} code accepted.")
            self.printServerInfo()
        else:
            self.sio.emit("codeDenied", room=sid)
            print(f"Client {sid} code denied.")
        
    def newUser(self, sid, data):
        print(f"Client {sid} player name set to {data}.")
        self.players[sid] = data
        self.printServerInfo()

# if __name__ == '__main__':
#     host = Host()
#     host.run()

# MAX_CONNECTIONS = 20
