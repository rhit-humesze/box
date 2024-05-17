import eventlet
import socketio
import threading
import base64
import os
import json

from queue import Queue

class Host:
    def __init__(self, code, join_q: Queue, disc_q: Queue, draw_q: Queue, vote_q: Queue, msg_q: Queue, image_prompts_q: Queue, text_prompts_q: Queue):
        self.sio = socketio.Server(cors_allowed_origins="*")
        self.app = socketio.WSGIApp(self.sio)
        self.players = {}
        self.gameCode = code
        self.server = None

        #outtake queue
        self.join_q = join_q
        self.disc_q = disc_q
        self.draw_q = draw_q
        self.image_prompts_q = image_prompts_q
        self.text_prompts_q = text_prompts_q
        self.vote_q = vote_q

        #test and image prompts (lists)
        self.prompts = []
        # current player for boxphone
        self.players_left = {}

        #intake queue
        self.msg_q = msg_q
        
        # init events
        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.on("gameCode", self.checkCode)
        self.sio.on("userName", self.newUser)
        self.sio.on("drawingSubmission", self.drawingSubmission)
        self.sio.on("drawingVote", self.drawingVote)
        self.sio.on("boxphoneImageSubmission", self.boxphoneImageSubmission)
        self.sio.on("boxphoneTextSubmission", self.boxphoneTextSubmission)
        
    def run(self):
        '''start the server'''
        # serv_thread = threading.Thread(target=self.start_server)
        # serv_thread.start()
        # serv_thread.join()
        self.start_server()
    
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
        # DEBUG CODE #
        self.sio.emit("boxphoneWait")
        self.players_left = dict(self.players)
        if len(self.players) >= 3:
            self.sio.emit("boxphoneFirstWrite", room=sid)
            self.players_left.pop(sid)
        # END DEBUG CODE #
        
    def drawingSubmission(self, sid, imageData, name):
        imageData = imageData.replace('data:image/png;base64,', '')
        img_data = str.encode(imageData)
        path = os.path.join(os.curdir, f"images/{sid}_{name}.png")
        # TODO need to add image/name to game and associate with sid
        with open(path, "wb") as fh:
            fh.write(base64.decodebytes(img_data))

    def boxphoneImageSubmission(self, sid, imageData):
        imageData = imageData.replace('data:image/png;base64,', '')
        print(f"Player {sid} submitted an image response")
        self.prompts.append(imageData)

        # store image
        img_data = str.encode(imageData)
        path = os.path.join(os.curdir, f"images/boxphone_{sid}.png")
        with open(path, "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        self.image_prompts_q.put({sid:path})
        print(f"Player {sid} submitted an image response")
        # tell current player to wait and next player to start writing
        self.sio.emit("boxphoneWait", room=sid)
        next_sid = self.getNextSid()
        if next_sid != 0:
            self.sio.emit("boxphoneWrite", imageData, room=next_sid)


    def boxphoneTextSubmission(self, sid, text):
        self.prompts.append(text)
        # store text
        self.text_prompts_q.put({sid: text})
        print(f"Player {sid} submitted a text response")
        # tell current player to wait and next player to start drawing
        self.sio.emit("boxphoneWait", room=sid)
        next_sid = self.getNextSid()
        if next_sid != 0:
            self.sio.emit("boxphoneDraw", text, room=next_sid)


    def getNextSid(self):
        # Get an sid, remove it, and return it
        if len(self.players_left) == 0:
            # Game is over, send results
            self.boxphone_results()
            return 0
        sid = list(self.players_left.keys())[0]
        self.players_left.pop(sid)
        return sid

    def boxphone_results(self):
        print("sending results")
        json_str = json.dumps(self.prompts)
        self.sio.emit("boxphoneResults", json_str)


    def drawingVote(self, sid, side):
        # TODO need to send 0 or 1 to game function
        if side == "left":
            return 0
        else:
            return 1
    
    def stop(self):
        '''safely stop the server'''
        if self.server:
            self.server.close()

