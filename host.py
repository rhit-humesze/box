import eventlet
import socketio
import threading
import base64
import os
from models import DrawingData

from queue import Queue

class Host:
    def __init__(self, code, join_q: Queue, disc_q: Queue, draw_q: Queue, vote_q: Queue, msg_q: Queue):
        self.sio = socketio.Server(cors_allowed_origins="*")
        self.app = socketio.WSGIApp(self.sio)
        self.players = {}
        self.gameCode = code
        self.server = None

        #outtake queue
        self.join_q = join_q
        self.disc_q = disc_q
        self.draw_q = draw_q
        self.vote_q = vote_q

        #intake queue
        self.msg_q = msg_q
        
        # init events
        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.on("gameCode", self.checkCode)
        self.sio.on("userName", self.newUser)
        self.sio.on("drawingSubmission", self.drawingSubmission)
        self.sio.on("drawingVote", self.drawingVote)
        
    def run(self):
        '''start the server'''
        serv_thread = threading.Thread(target=self.start_server)
        serv_thread.start()

        msg_handler_thread = threading.Thread(target=self.server_message_handler)
        msg_handler_thread.start()
        # serv_thread.join()
        # self.start_server()
    
    def server_message_handler(self):
        while True:
            if not self.msg_q.empty():
                msg = self.msg_q.get()
                print(msg)

    def start_server(self):
        self.server = eventlet.wrap_ssl(eventlet.listen(('', 5100)), 
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
        
    def drawingSubmission(self, sid, imageData, name):
        imageData = imageData.replace('data:image/png;base64,', '')
        img_data = str.encode(imageData)
        filepath = f"images/{sid}_{name}.png"
        path = os.path.join(os.curdir, filepath)
        with open(path, "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        drawing = DrawingData(filepath, name, self.players[sid])
        self.draw_q.put({sid:drawing})
    
    def drawingVote(self, sid, side):
        if(side == "left"):
            self.vote_q.put({sid:int(0)})
        else:
            self.vote_q.put({sid:int(1)})
    
    def stop(self):
        '''safely stop the server'''
        if self.server:
            self.server.close()