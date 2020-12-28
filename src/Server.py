import socket
from threading import Thread
import struct
import time


class Server:

    def __init__(self):
        self.ServerIp = socket.gethostbyname(socket.gethostname())
        self.BroadcastUdpPort = 13117
        self.TcpPort = 50000
        self.bufferSize = 1024

        msgFromServer = "Hello UDP Client"
        self.bytesToSend = str.encode(msgFromServer)
        self.client = {}

    def sendOffers(self, UDPServerSocket):
        counter = 0
        while True:
            msg = struct.pack('IbH', 0xfeedbeef, 0x2, self.TcpPort)
            # print(struct.unpack('IbH', msg))
            dest = ('<broadcast>', self.BroadcastUdpPort)
            UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            print('sends packet... ')  # Todo: delete that print
            print(f'udpPort: {self.BroadcastUdpPort}. tcpPort: {self.TcpPort}')
            print(f'ServerIp: {self.ServerIp}')

            UDPServerSocket.sendto(msg, dest)
            counter += 1
            time.sleep(1)
            if counter == 10:
                break

    def replyToMessages(self):

        # socket.accept()
        # Accept a connection. The socket must be bound to an address and listening for connections.
        # The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data on the connection,
        # and address is the address bound to the socket on the other end of the connection.

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((socket.gethostname(), self.TcpPort))
        s.listen(5)

        while True:
            clientsocket, address = s.accept()
            # now our endpoint knows about the OTHER endpoint.
            print(f"Connection from {address} has been established.")
            clientsocket.send(bytes("Hey there!!!", "utf-8"))
            clientsocket.close()


        """
        timeout = time.time() + 10
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # UDPServerSocket.bind((self.ServerIp, self.TcpPort))
        UDPServerSocket.bind(('', self.TcpPort))
        while True:
            if time.time() > timeout:
                break
            bytesAddressPair = UDPServerSocket.recvfrom(self.bufferSize)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
            request = struct.unpack('IbH', message)
            if (request[0], request[1]) == (4276993775, 2):
                TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                TCPServerSocket.bind((self.ServerIp, request[2]))
                TCPServerSocket.listen(1)
                conn, address = TCPServerSocket.accept()
            clientMsg = "Message from Client:{}".format(message)
            clientIP = "Client IP Address:{}".format(address)
            print(clientMsg)
            print(clientIP)
            # Sending a reply to client
            # UDPServerSocket.sendto(self.bytesToSend, address)
        """

    def createUDPSocket(self):
        # Create a datagram socket
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Bind to address and ip
        UDPServerSocket.bind((self.ServerIp, self.BroadcastUdpPort))
        print(f'Server started, listening on IP address {self.ServerIp}')

        # Send offers
        offersThread = Thread(target=self.sendOffers, args=(UDPServerSocket,))
        offersThread.start()

        # Listen for incoming datagrams
        replyThread = Thread(target=self.replyToMessages, args=())
        replyThread.start()


if __name__ == '__main__':
    server = Server()
    server.createUDPSocket()