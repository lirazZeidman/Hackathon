from src.Client import *
from socket import *


class Server:

    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = 13117

    def UDPServer(self):
        serverPort = self.port
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(('', serverPort))
        print("the server ready to recieve")
        while 1:
            massege, clientAdd = serverSocket.recvfrom(2048)
            # fuction that the serverUDP do ********
            modifiedMessage = massege.upper()
            serverSocket.sendto(modifiedMessage, clientAdd)

    def TCPServer(self):
        serverPort = self.port
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(('', serverPort))
        serverSocket.listen(1)
        print("the server ready to recieve")
        while 1:
            connectionSocket, addr = serverSocket.accept()

            sentence = connectionSocket.recv(1024)
            capitalizeSentence = sentence.upper()
            connectionSocket.close()
