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
        self.clients = {}
        self.clients2 = {}

    def sendOffers(self, UDPServerSocket):
        counter = 0
        while True:
            if counter < 10:
                msg = struct.pack('IbH', 0xfeedbeef, 0x2, self.TcpPort)
                # print(struct.unpack('IbH', msg))
                dest = ('<broadcast>', self.BroadcastUdpPort)
                UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                print('sends packet... ')  # Todo: delete that print
                UDPServerSocket.sendto(msg, dest)
                counter += 1
                time.sleep(1)
            else:
                break

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

    """def replyToMessages(self):"""

    #   def replyToMessages(self):
    #     timeout = time.time() + 10
    #
    #     # socket.accept()
    #     # Accept a connection. The socket must be bound to an address and listening for connections.
    #     # The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data on the connection,
    #     # and address is the address bound to the socket on the other end of the connection.
    #
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     s.settimeout(10)
    #     # s.bind((socket.gethostname(), self.TcpPort))
    #     s.bind(('0.0.0.0', self.TcpPort))
    #     s.listen(5)
    #
    #     clientsocket, address = s.accept()
    #     print('socket name: ', clientsocket.getsockname())
    #     clientsocket.settimeout(10)
    #     # print('address: ', clientsocket.__str__())
    #     # now our endpoint knows about the OTHER endpoint.
    #     self.clients[address] = clientsocket  # dict contains: (ip,port)->TCP connection
    #     print(f"Connection from {address} has been established.")
    #
    #     stopped = False
    #     while not stopped:
    #         try:
    #             data = clientsocket.recvfrom(self.bufferSize)
    #             print("received data: ", data)
    #             clientsocket.send(bytes("Hey there!!! its me, the server :)", "utf-8"))
    #
    #
    #         except socket.timeout:
    #             print('time out reached, replyToMessages')
    #             stopped = True
    #
    #     # clientsocket.close()
    #     """
    #     timeout = time.time() + 10
    #     UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    #     # UDPServerSocket.bind((self.ServerIp, self.TcpPort))
    #     UDPServerSocket.bind(('', self.TcpPort))
    #     while True:
    #         if time.time() > timeout:
    #             break
    #         bytesAddressPair = UDPServerSocket.recvfrom(self.bufferSize)
    #         message = bytesAddressPair[0]
    #         address = bytesAddressPair[1]
    #         request = struct.unpack('IbH', message)
    #         if (request[0], request[1]) == (4276993775, 2):
    #             TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             TCPServerSocket.bind((self.ServerIp, request[2]))
    #             TCPServerSocket.listen(1)
    #             conn, address = TCPServerSocket.accept()
    #         clientMsg = "Message from Client:{}".format(message)
    #         clientIP = "Client IP Address:{}".format(address)
    #         print(clientMsg)
    #         print(clientIP)
    #         # Sending a reply to client
    #         # UDPServerSocket.sendto(self.bytesToSend, address)
    #     """

    def createUDPSocket(self):
        # Create a datagram socket

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # UDPServerSocket.settimeout(10)
        # Bind to address and ip
        UDPServerSocket.bind((self.ServerIp, self.BroadcastUdpPort))
        print(f'Server started, listening on IP address {self.ServerIp}')

        # Send offers
        offersThread = Thread(target=self.sendOffers, args=(UDPServerSocket,))
        offersThread.daemon = True
        offersThread.start()

        # Listen for incoming datagrams
        replyThread = Thread(target=self.replyToMessages, args=())
        replyThread.daemon = True
        replyThread.start()

        # Wait for at most 10 seconds for the thread to complete.
        offersThread.join(10)
        replyThread.join(10)
        # Always signal the event. Whether the thread has already finished or not,
        # the result will be the same.

    def replyToMessages(self):
        # timeout = time.time() + 10

        # socket.accept()
        # Accept a connection. The socket must be bound to an address and listening for connections.
        # The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data on the connection,
        # and address is the address bound to the socket on the other end of the connection.

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(10)
        # s.bind((socket.gethostname(), self.TcpPort))
        s.bind(('0.0.0.0', self.TcpPort))
        s.listen(5)

        replyMultiMessagesThread = Thread(target=self.replyToMessagesThread, args=(s,))
        replyMultiMessagesThread.start()


        # clientsocket.close()

    def replyToMessagesThread(self, sSocket):
        clientsocket, address = sSocket.accept()
        print('socket name: ', clientsocket.getsockname())
        clientsocket.settimeout(10)
        # print('address: ', clientsocket.__str__())
        # now our endpoint knows about the OTHER endpoint.
        self.clients[address] = clientsocket  # dict contains: (ip,port)->TCP connection
        print(f"Connection from {address} has been established.")

        for c in self.clients2.values():
            c.close()
        self.clients2 = {}

        stopped = False
        while not stopped:
            try:
                conn, address = sSocket.accept()
                self.clients2[address] = conn
                sSocket.setblocking(1)  # prevents timeout
                data = clientsocket.recvfrom(self.bufferSize)
                print("received data: ", data)
                clientsocket.send(bytes("Hey there!!! its me, the server :)", "utf-8"))

                print("\nConnection has been established! from :" + address)

            except socket.timeout:  # todo check if to erase the type of the e - socket.timeout
                print('time out reached, replyToMessagesThread')
                stopped = True


    def start_turtle(self):
        while True:
            cmd = input('turtle> ')
            if cmd == 'list':
                self.list_connections()
            else:
                print("Command not recognized")

    def list_connections(self):
        results = ''

        for i, add, conn in enumerate(self.clients2.items()):
            try:
                conn.send(str.encode(' '))
                conn.recv(20480)
            except:
                self.clients2 = {}
                continue

            results = str(i) + "   " + str(add) + "\n"

        print("----Clients----" + "\n" + results)

    def send_target_commands(self, conn):
        while True:
            try:
                cmd = input()
                if cmd == 'quit':
                    break
                if len(str.encode(cmd)) > 0:
                    conn.send(str.encode(cmd))
                    client_response = str(conn.recv(20480), "utf-8")
                    print(client_response, end="")
            except:
                print("Error sending commands")


if __name__ == '__main__':
    server = Server()
    server.createUDPSocket()
    print("Clients ->", server.clients)
