from socket import *
from keyboard import *


class Client:

    def __init__(self, port = 13117):
        self.ip = gethostbyname(gethostname())
        self.port = port


    def UDPClient(self):
        serverName = 'hostname'
        serverPort = self.port
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        message = input('Hello im Client')
        clientSocket.sendto(message, (serverName, serverPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        print(modifiedMessage)
        clientSocket.close()

    def TCPClient(self):
        serverName = 'servername'
        serverPort = self.port
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        message = input('Hello im Client')
        clientSocket.connect((serverName, serverPort))
        sentence = input('name of my group is QueenGambit')
        clientSocket.send(sentence)
        modifiedSentence = clientSocket.recv(1024)
        print('from server: ', modifiedSentence)
        clientSocket.close()


    def connetcingToServer(self):
        pass

