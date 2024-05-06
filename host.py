# from game import Game
# from player import Player
import socket
import sys
import eventlet
import socketio

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('[INFO] Connect to client', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    
@sio.on("userName")
def newUser(sid, data):
    print(data)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5100)), app)

# MAX_CONNECTIONS = 20


# class Host:
#     def __init__(self):
#         self.players = []
#         self.game = None

#     def add_player(self, conn_socket, client_num):
#         new_player = Player(conn_socket)
#         new_player.set_name("Player " + client_num)
#         self.players.append(new_player)

#     def remove_player(self, index):
#         self.players.remove(index)

#     def start_game(self, game_type):
#         if self.game != None:
#             print("Game already started!")
#             return "Game already started!"
#         if game_type == "1":
#             # start game type 1
#             self.game = Game()

#     def host_program(self):
#         host_name = socket.gethostname()
#         host_ip = socket.gethostbyname(host_name)

#         print("Host name: ", str(host_name))
#         print("Host IP: ", str(host_ip))

#         if (len(sys.argv) != 2):
#             print("Usage: python host.py <port_number>")
#             sys.exit()

#         # unsigned short
#         server_port = int(sys.argv[1])

#         # Create Socket
#         server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         # Forces socket to be able to be used even if already in use
#         server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         # Bind Socket
#         server_socket.bind(('', server_port))
#         server_socket.listen(MAX_CONNECTIONS)

#         client_num = 1

#         while True:
#             # sit and wait for connection
#             # in python it will return 2 different things (new socket and address of the client that tried to connect)
#             # USE THIS SOCKET NOW (different port number, doesn't matter)
#             conn_socket, address = server_socket.accept()

#             print("Connection ", str(client_num), " made from ", str(address))

#             # need comma after last
#             self.add_player(conn_socket, client_num)

#             client_num += 1

#         server_socket.close()


# if __name__ == "__main__":
#     host = Host()
#     host.host_program()
#     # game = Game()
#     # game.game_loop()
#     # game.add_player("chungus")
