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
        self.group1 = {}
        self.group2 = {}

    def sendOffers(self, UDPServerSocket):
        counter = 0
        while True:
            if counter < 10:
                msg = struct.pack('IbH', 0xfeedbeef, 0x2, self.TcpPort)
                # print(struct.unpack('IbH', msg))
                dest = ('<broadcast>', self.BroadcastUdpPort)
                UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
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

    """def createUDPSocket(self):"""

    # def createUDPSocket(self):
    # # Create a datagram socket
    #
    # UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # # UDPServerSocket.settimeout(10)
    # # Bind to address and ip
    # UDPServerSocket.bind((self.ServerIp, self.BroadcastUdpPort))
    # print(f'Server started, listening on IP address {self.ServerIp}')
    #
    # # Send offers
    # offersThread = Thread(target=self.sendOffers, args=(UDPServerSocket,))
    # offersThread.start()
    #
    # # Listen for incoming datagrams
    # replyThread = Thread(target=self.replyToMessages, args=())
    # replyThread.start()
    #
    # # Wait for at most 10 seconds for the thread to complete.
    # offersThread.join(10)
    # replyThread.join(10)
    # # Always signal the event. Whether the thread has already finished or not,
    # # the result will be the same.

    def createUDPSocket(self):
        # Create a datagram socket

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # UDPServerSocket.settimeout(10)
        # Bind to address and ip
        UDPServerSocket.bind((self.ServerIp, self.BroadcastUdpPort))
        print(f'Server started, listening on IP address {self.ServerIp}')

        # Send offers
        offersThread = Thread(target=self.sendOffers, args=(UDPServerSocket,))
        offersThread.start()

        # Listen for incoming datagrams
        replyThread = Thread(target=self.replyToMessages, args=())
        replyThread.start()

        # Wait for at most 10 seconds for the thread to complete.
        offersThread.join(10)
        replyThread.join(10)
        # Always signal the event. Whether the thread has already finished or not,
        # the result will be the same.

    def replyToMessages(self):
        for c in self.clients.values():
            c.close()
        self.clients = {}
        self.group1 = {}
        self.group2 = {}

        stopped = False
        while not stopped:
            try:
                # creating socket
                sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sSocket.settimeout(10)

                # binding socket
                # s.bind((socket.gethostname(), self.TcpPort))
                sSocket.bind(('0.0.0.0', self.TcpPort))
                sSocket.listen(5)

                # connecting clients
                clientsocket, address = sSocket.accept()
                # print('socket name: ', clientsocket.getsockname()) # todo delete that print
                # clientsocket.settimeout(10)  #  todo check if need - its setting timeout on the clients connection - remove ?

                # todo get the names of the clients!!!
                self.clients[address] = clientsocket
                # self.clients[address] = clientsocket  # dict contains: (ip,port)->TCP connection
                # print(f"Connection from {address} has been established.") # todo delete that print
                sSocket.setblocking(1)  # prevents timeout

                # data = clientsocket.recvfrom(self.bufferSize) # i dont send nothing no more
                # print("received data: ", data)  #todo delete that print
                # clientsocket.send(bytes("Hey there!!! its me, the server :)", "utf-8"))  # todo delete that packet send!!

                # print("Connection has been established! from :", address) #todo delete that print

            except socket.timeout:  # todo check if to erase the type of the e - socket.timeout
                # print('time out reached, replyToMessages') # todo delete that print
                stopped = True

    def printGroup1(self):
        g1 = ""
        for add, conn in self.group1:
            g1 += str(add) + "\n"
        return g1

    def printGroup2(self):
        g2 = ""
        for add, conn in self.group2:
            g2 += str(add) + "\n"
        return g2

    def handleGroupsDividing(self):
        for i, tup in enumerate(self.clients.items()):
            add, conn = tup
            if len(self.clients) / 2 > i:
                self.group1[add] = conn
            else:
                self.group2[add] = conn

    def handleGameAnnouncement(self):
        for i, tup in enumerate(self.clients.items()):
            add, conn = tup
            add, conn = tup
            msg = f'Welcome to Keyboard Spamming Battle Royale.\n' \
                  f'Group 1:\n' \
                  f'==\n' \
                  f'{self.printGroup1()}\n' \
                  f'Group 2:\n' \
                  f'==\n' \
                  f'{self.printGroup2()}\n'
            conn.send(bytes(msg, 'utf-8'))

    def start_turtle(self):
        while True:
            cmd = input('turtle> ')
            if cmd == 'list':
                self.list_connections()
            else:
                print("Command not recognized")

    def list_connections(self):
        results = ''

        for i, add, conn in enumerate(self.clients.items()):
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
    print("\nClients ->", server.clients)
    server.handleGroupsDividing()
    print("\ngroup 1 ->", server.group1)
    print("\ngroup 2 ->", server.group2)
    server.handleGameAnnouncement()
