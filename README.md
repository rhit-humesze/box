# box: https://github.com/rhit-humesze/box

Box is a asgi game application inspired by Jackbox. A host starts a game on their machine and players connect via a web client that we host at bocks-d6c5c.web.app using Firebase. We use SLL to encrypt and decrypt data sent from socket connections over the Internet. Because we do not have access to a verified SSL certificate, we create our own. At this stage players will need to manually verify the certificate from their console.

We use socket.io to receive data asynchronously over socket connections. Queues (threadsafe) are used to pipe data between threads.

## main.py
Entry point for creating game. When main.py is run, a host server and the game are spawned as separate threads. 

## game.py
Contains the Game class that handles all of the game logic. 

## host.py
Contains the Host class which spawns the asgi server. Contains logic for broadcasting soi signals.
