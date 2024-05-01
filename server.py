import socket
import sys
import threading
import os.path

from game import Game
from lobby import Lobby

SIZE = 1024

def server_program():
    host = socket.gethostname()
    host_ip = socket.gethostbyname(host)

    print("Host name: ", str(host))
    print("Host IP: ", str(host_ip))

    if(len(sys.argv) != 2):
        print("Usage: python server.py <port_number>")
        sys.exit()

    # unsigned short
    port = int(sys.argv[1])

    # Create
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # forces socket to be able to be used even if already in use
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind (something about this only works for python)
    server_socket.bind(('', port))
    # Listen (5 is how many it will listen to)
    server_socket.listen(5)

    client_num = 1

    while True:
        # sit and wait for connection
        # in python it will return 2 different things (new socket and address of the client that tried to connect)
        # USE THIS SOCKET NOW (different port number, doesn't matter)
        conn_socket, address = server_socket.accept()

        print("Connection ", str(client_num), " made from ", str(address))

        # need comma after last
        t = threading.Thread(target=server_thread, args=(conn_socket, client_num,))
        t.start()

        client_num += 1

    server_socket.close()

    def server_thread(client_socket, client_num):
        while True:
            # it wont just send all if u do big number, it will break it up
            # decode puts in utf-8 format (string)
            # this is where client sends first
            print("Listening for client request")
            request = client_socket.recv(SIZE).decode()

            # times out or client left: received null
            if (not request) or (request.lower().strip() == ';;;'):
                break
            else:
                print("Received request from client: ", str(client_num), str(request))
                handle_request(client_socket, request)

    client_socket.close()

    def handle_request(socket, request):
        space_index = request.find(" ")
        request_type = request[:space_index]
        request_args = request[space_index:]
        lobbies = []
        if request_type == "createLobby":
            lobby = Lobby()
            lobbies.append(lobby)
            joinLobby(socket, lobbyName)
        elif request_type == "joinLobby":
            joinLobby(socket, request_args)
        elif request_type == "leaveLobby":
            leaveLobby(socket, request_args)
        elif request_type == "startGame":
            # called when all the players have joined
            # get lobby object
            # start the game loop for the lobby object
        else:
            print("That just ain't right!")
            socket.send("0".encode())

    def createLobby(socket, lobby_name):
        # Each lobby would have a game, a list of users and their connection sockets
        lobby = Lobby(lobby_name)

    def joinLobby(socket, args):