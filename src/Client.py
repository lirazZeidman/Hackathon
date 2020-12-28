import socket


class Client:

    def __init__(self, port):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port


    def lookingForServer(self):
        pass


    def connetcingToServer(self):
        pass

