import socket
import struct
import time
from threading import Thread

PORTNUMBER = 13117
class Client:
    def __init__(self, teamName):
        global PORTNUMBER
        self.clientIP = socket.gethostbyname(socket.gethostname())
        self.clientUdpPort = 13117
        self.teamName = teamName
        self.bufferSize = 1024
        self.serverIP = None
        self.serverPort = None

        print('Client started, listening for offer requests...')

        msgFromClient = "Hello UDP Server"
        self.bytesToSend = str.encode(msgFromClient)

        # PORTNUMBER += 1

    def LookForServer(self):
        # serverAddressPort = ("127.0.0.1", 20001)

        # Create a UDP socket at client side
        timeout = time.time() + 10
        while True:
            UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPClientSocket.settimeout(10)
            UDPClientSocket.bind(('', self.clientUdpPort))

            try:
                offer, (self.serverIP, server_port) = UDPClientSocket.recvfrom(1024)
                # (b'\xef\xbe\xed\xfe\x02\x00P\xc3', ('192.168.56.1', 13117))
                offer = struct.unpack('IbH', offer)

                if (offer[0], offer[1]) == (4276993775, 2):
                    self.serverPort = offer[2]
                    print(f'Received offer from {self.serverIP}, attempting to connect...')
                    self.createTcpConnection(offer)
                    break
            except socket.timeout:  # todo delete the except
                print('timeout reached, LookForServer')


    def createTcpConnection(self, offer):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print("clientIP - ", self.clientIP, " serverIP - ", self.serverIP, " serverPort - ", self.serverPort) #todo delete that print
        # s.settimeout(10)  # TODO: delete this later
        s.connect((self.serverIP, self.serverPort))
        s.send(bytes(f'{self.teamName}', 'utf-8'))
        # print('socket.gethostname(): ', socket.gethostname())
        # print('self.serverPort: ', self.serverPort)

        try:
            while True:
                # s.listen(5)
                msg = s.recv(1024)
                msg = msg.decode("utf-8")
                if len(msg)>0:
                    print(msg)

        except socket.timeout:
            print('tcp-connection timeout has reached') #todo delete that print
            s.close()


def startClients(name):
    client1 = Client(name)
    client1.LookForServer()


if __name__ == '__main__':
    client = Client("QueenGambit")
    client.LookForServer()

