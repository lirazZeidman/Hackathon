import socket
from threading import Thread
import struct
import time


class Server:

    def __init__(self):
        # self.ServerIp = socket.gethostbyname(socket.gethostname())
        self.ServerIp = ""
        self.BroadcastUdpPort = 13117
        self.TcpPort = 50000
        self.bufferSize = 1024

        msgFromServer = "Hello UDP Client"
        self.bytesToSend = str.encode(msgFromServer)
        self.client = {}

    def createUDPSocket(self):
        # Create a datagram socket
        UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPServerSocket.settimeout(10)

        # Bind to address and ip
        UDPServerSocket.bind((self.ServerIp, self.BroadcastUdpPort))

        print(f'Server started, listening on IP address {self.ServerIp}')

        # Send offers
        offersThread = Thread(target=self.sendOffers, args=(UDPServerSocket,))
        offersThread.start()

        # Listen for incoming datagrams
        replyThread = Thread(target=self.replyToMessages, args=())
        replyThread.start()

    def sendOffers(self, UDPServerSocket):
        counter = 0

        while True:
            msg = struct.pack('IbH', 0xfeedbeef, 0x2, self.TcpPort)
            # print(struct.unpack('IbH', msg))
            dest = ('<broadcast>', self.BroadcastUdpPort)
            UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            print('sends packet... ')  # Todo: delete that print
            UDPServerSocket.sendto(msg, dest)  # TODO: check if that what makes the problem between computers.
            counter += 1
            time.sleep(1)
            if counter == 10:
                break

        UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0)

    def replyToMessages(self):

        # socket.accept()
        # Accept a connection. The socket must be bound to an address and listening for connections.
        # The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data on the connection,
        # and address is the address bound to the socket on the other end of the connection.

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ServerIp, self.TcpPort))
        s.listen(64)

        timeout = time.time() + 10
        clientsocket = None
        while True:

            if s.accept() is not None:
                clientsocket, address = s.accept()
                # now our endpoint knows about the OTHER endpoint.
                print(f"Connection from {address} has been established.")
                clientsocket.send(bytes("Hey there!!!", "utf-8"))

            if time.time() > timeout:
                break
        if clientsocket:
            clientsocket.close()


if __name__ == '__main__':
    server = Server()
    server.createUDPSocket()
