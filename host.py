import eventlet
import socketio
import base64
import os
import re
from models import DrawingData
from queue import Queue

class Host:
    def __init__(self, code, join_q: Queue, disc_q: Queue, draw_q: Queue, vote_q: Queue, msg_q: Queue):
        self.sio = socketio.Server(cors_allowed_origins="*")
        self.app = socketio.WSGIApp(self.sio)
        self.players = {}
        self.gameCode = code
        self.server = None

        # outtake queue
        self.join_q = join_q
        self.disc_q = disc_q
        self.draw_q = draw_q
        self.vote_q = vote_q

        # intake queue
        self.msg_q = msg_q
        
        # init events
        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.on("gameCode", self.checkCode)
        self.sio.on("userName", self.newUser)
        self.sio.on("drawingSubmission", self.drawingSubmission)
        self.sio.on("drawingVote", self.drawingVote)
        
    def run(self):
        '''start the server and the message handler in the same thread'''
        eventlet.spawn(self.server_message_handler)
        self.start_server()
    
    def server_message_handler(self):
        while True:
            if not self.msg_q.empty():
                msg = self.msg_q.get()
                if msg == 0:
                    self.sio.emit("drawSomeDraw")
                    # print("\nstarting drawing round\n")
                elif msg == 1:
                    self.sio.emit("timesUp")
                    # print("\nTIMES UP!!!\n")
                elif msg == 2:
                    self.sio.emit("drawSomeVote")
                    # print("\nstarting voting round\n")
                elif msg == 3:
                    self.sio.emit("awesomeSauce")
                    # print("\nstarting voting round\n")
                else:
                    self.sio.emit("gameOver")
                    # filepath = f"images"
                    # path = os.path.join(os.curdir, filepath)
                    # for drawing in os.listdir(path):
                    #     if(drawing != msg):
                    #         drawingPath = os.path.join(filepath, drawing)
                    #         os.remove(drawingPath)
                    # print("\nending game\n")
                    
            eventlet.sleep(0.1)  # Sleep briefly to prevent a tight loop

    def start_server(self):
        os.makedirs("images", exist_ok=True)
        if not os.environ.get("NO_TLS") and not (os.path.exists('./host.cert') and os.path.exists('./host.key')):
            raise FileNotFoundError("host.cert / host.key not found. Create them (e.g. with mkcert) "
                                    "or set NO_TLS=1 when running behind a tunnel.")
        sock = eventlet.listen(('0.0.0.0', 5100))
        if not os.environ.get("NO_TLS"):
            sock = eventlet.wrap_ssl(sock, certfile='./host.cert',
                                    keyfile='./host.key', server_side=True)
        self.server = sock
        eventlet.wsgi.server(self.server, self.app, log_output=False)

    def printServerInfo(self):
        print(f"\nBox code: {self.gameCode}\n")
        print(f"Players: {list(self.players.values())}")

    def connect(self, sid, env):
        print(f"New client {sid} connected.")
        self.printServerInfo()

    def disconnect(self, sid):
        name = self.players.pop(sid, None)
        print(f"Client {sid} ({name}) disconnected.")
        if name is not None:
            self.disc_q.put(sid)
        self.printServerInfo()

    def checkCode(self, sid, data):
        print(f"Received game code {data} from connected client {sid}.")
        if data == self.gameCode:
            self.sio.emit("codeAccepted", room=sid)
            print(f"Client {sid} code accepted.")
            self.printServerInfo()
        else:
            self.sio.emit("codeDenied", room=sid)
            print(f"Client {sid} code denied.")
        
    def newUser(self, sid, data):
        print(f"Client {sid} player name set to {data}.")
        self.players[sid] = data
        self.join_q.put({sid: data})
        self.printServerInfo()
        
    def drawingSubmission(self, sid, imageData, name):
        if sid not in self.players:
            return
        if not isinstance(imageData, str) or not isinstance(name, str):
            return
        name = name[:20]
        try:
            raw = base64.b64decode(imageData.replace('data:image/png;base64,', ''), validate=True)
        except Exception:
            return
        if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
            return  # not a PNG; don't write it or let pygame try to load it
        safe = re.sub(r'[^A-Za-z0-9_]', '_', name)
        filepath = f"images/{sid}_{safe}.png"
        path = os.path.join(os.curdir, filepath)
        with open(path, "wb") as fh:
            fh.write(raw)
        drawing = DrawingData(filepath, name, self.players[sid])
        self.draw_q.put({sid: drawing})

    def drawingVote(self, sid, side):
        if sid not in self.players:
            return
        if side == "left":
            self.vote_q.put({sid: int(0)})
        else:
            self.vote_q.put({sid: int(1)})
    
    def stop(self):
        '''safely stop the server'''
        if self.server:
            self.server.close()