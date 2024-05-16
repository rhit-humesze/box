import eventlet
import socketio

from queue import Queue

class Host:
    def __init__(self, code, join_q: Queue, disc_q: Queue, draw_q: Queue):
        self.sio = socketio.Server(cors_allowed_origins="*")
        self.app = socketio.WSGIApp(self.sio)
        self.players = {}
        self.gameCode = code
        self.server = None
        self.join_q = join_q
        self.disc_q = disc_q
        self.draw_q = draw_q
        
        # init events
        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.on("gameCode", self.checkCode)
        self.sio.on("userName", self.newUser)
        
    def run(self):
        '''start the server'''
        self.server = eventlet.wrap_ssl(eventlet.listen(('0.0.0.0', 5100)), 
                                        certfile='./host.cert', 
                                        keyfile='./host.key', 
                                        server_side=True)
        eventlet.wsgi.server(self.server, self.app, log_output=False)

    def printServerInfo(self):
        print(f"\nBox code: {self.gameCode}\n")
        print(f"Players: {list(self.players.values())}")

    def connect(self, sid, env):
        print(f"New client {sid} connected.")
        self.players[sid] = f"Player {len(self.players) + 1}"
        self.printServerInfo()

    def disconnect(self, sid):
        print(f"Client {sid} ({self.players[sid]}) disconnected.")
        self.players.pop(sid)
        self.disc_q.put(sid)
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
        self.join_q.put({sid:data})
        self.printServerInfo()
    
    def stop(self):
        '''safely stop the server'''
        if self.server:
            self.server.close()