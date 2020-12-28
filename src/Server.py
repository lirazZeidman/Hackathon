from src.Client import *


class Server:

    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port
