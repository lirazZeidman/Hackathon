import socket
from threading import Thread
import struct
import time
from StopableThread import StoppableThread


class Server:

    def __init__(self):
        self.ServerIp = socket.gethostbyname(socket.gethostname())
        self.BroadcastUdpPort = 13117
        self.TcpPort = 50000
        self.bufferSize = 1024

        self.clients = {}
        self.group1 = {}
        self.group2 = {}

        self.scoreGroup1 = {}
        self.scoreGroup2 = {}

    def createUDPSocket(self):
        # Create a datagram socket

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # UDPServerSocket.setTimeout(10)
        # Bind to address and ip
        UDPServerSocket.bind((self.ServerIp, self.BroadcastUdpPort))
        UDPServerSocket.settimeout(10)
        print(f'Server started, listening on IP address {self.ServerIp}')
        # print("  UDPServerSocket.gettimeout(): ",UDPServerSocket.gettimeout())
        # print("in   ", time.time())

        # Send offers
        offersThread = Thread(target=self.sendOffers, args=(UDPServerSocket,))
        offersThread.start()

        # Listen for incoming datagrams
        replyThread = Thread(target=self.replyToMessages, args=(time.time() + 10,))
        replyThread.start()

        # Wait for at most 10 seconds for the thread to complete.
        offersThread.join(10)
        replyThread.join(10)
        # Always signal the event. Whether the thread has already finished or not,
        # the result will be the same.

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

    def replyToMessages(self, MaxTime):
        for c in self.clients.values():
            c[0].close()
        self.clients = {}
        self.group1 = {}
        self.group2 = {}

        stopped = False
        while not stopped:
            try:
                # creating socket
                sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if MaxTime - time.time() < 0:
                    break

                sSocket.settimeout(int(MaxTime - time.time()))

                # binding socket
                # s.bind((socket.gethostname(), self.TcpPort))
                sSocket.bind(('0.0.0.0', self.TcpPort))
                sSocket.listen(1)

                # connecting clients
                clientsocket, address = sSocket.accept()

                clientName = clientsocket.recv(1024).decode("utf-8")

                self.clients[address] = (clientsocket, clientName)
                # self.clients[address] = clientsocket  # dict contains: (ip,port)->TCP connection
                sSocket.setblocking(True)  # prevents timeout

                # data = clientsocket.recvfrom(self.bufferSize) # i dont send nothing no more

            except socket.timeout:  # todo check if to erase the type of the e - socket.timeout
                stopped = True

    def handleStartGame(self):
        msg = f'Welcome to Keyboard Spamming Battle Royal.\n' \
              f'Group 1:\n' \
              f'==\n' \
              f'{self.printGroup1()}\n' \
              f'Group 2:\n' \
              f'==\n' \
              f'{self.printGroup2()}\n'
        self.handleGameAnnouncements(msg)

        handleGameThread_1 = None
        handleGameThread_2 = None

        timeoutOfGame = time.time() + 10
        for adder, (conn, name) in self.clients.items():
            if adder in self.group1.keys():
                handleGameThread_1 = StoppableThread(target=self.handleGameThread_1,
                                                     args=(adder, conn))
                handleGameThread_1.start()
            if adder in self.group2.keys():
                handleGameThread_2 = StoppableThread(target=self.handleGameThread_2,
                                                     args=(adder, conn))
                handleGameThread_2.start()
        if handleGameThread_1 is not None:
            # handleGameThread_1.stop()
            handleGameThread_1.join(10)
        if handleGameThread_2 is not None and timeoutOfGame < time.time():
            # handleGameThread_2.stop()
            handleGameThread_2.join(10)

        Score1 = sum(self.scoreGroup1.values())
        Score2 = sum(self.scoreGroup2.values())
        msg = f'Game Over!\nGroup 1 typed in {Score1} characters. Group 2 typed in {Score2} characters.\n'
        winG = ""
        if Score2 > Score1:
            msg += 'Group 2 wins!\n'
            winG = self.printGroup2()
        if Score2 < Score1:
            msg += 'Group 1 wins!\n'
            winG = self.printGroup1()
        else:
            msg += 'It\'s a tie!\n'
        msg += "Congratulations to the winners:\n==\n" + winG

        self.handleGameAnnouncements(msg)
        print("Score1: ", Score1, " Score2: ", Score2)

    def handleGameThread_1(self, adder, conn):
        self.scoreGroup1[adder] = 0
        while True:

            char = conn.recv(1024)
            if len(char) > 0:
                self.scoreGroup1[adder] += 1

    def handleGameThread_2(self, adder, conn):
        self.scoreGroup2[adder] = 0
        while True:
            char = conn.recv(1024)
            if len(char) > 0:
                self.scoreGroup2[adder] += 1

    def printGroup1(self):
        g1 = ""
        for add, (conn, name) in self.group1.items():
            g1 += str(name) + "\n"
        return g1

    def printGroup2(self):
        g2 = ""
        for add, (conn, name) in self.group2.items():
            g2 += str(name) + "\n"
        return g2

    def handleGroupsDividing(self):
        for i, tup in enumerate(self.clients.items()):
            add, (conn, name) = tup
            if len(self.clients) / 2 > i:
                self.group1[add] = (conn, name)
            else:
                self.group2[add] = (conn, name)

    def handleGameAnnouncements(self, msg):
        for i, tup in enumerate(self.clients.items()):
            add, (conn, name) = tup
            conn.send(bytes(msg, 'utf-8'))


if __name__ == '__main__':
    server = Server()
    while True:
        server.createUDPSocket()
        # print("\nClients ->", server.clients)
        server.handleGroupsDividing()
        # print()
        # server.handleGameAnnouncement()
        if len(server.clients.keys()) > 0:
            server.handleStartGame()
        else:
            break
