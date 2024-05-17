## box

Box is a wsgi game application inspired by Jackbox. 

When the game is run (main.py), a host server and the game are spawned as separate threads. Players connect via a web client that we host at bocks-d6c5c.web.app using Firebase.

We use socket.io to receive data asynchronously over socket connections.