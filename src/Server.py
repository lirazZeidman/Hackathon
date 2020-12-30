import socket
from threading import Thread
import struct
import time
import select
from multiprocessing import Pool


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

        self.scoreGroup1 = {}
        self.scoreGroup2 = {}

        # UDPServerSocket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 10000))

    def createUDPSocket(self):
        # Create a datagram socket

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # UDPServerSocket.settimeout(10)
        # Bind to address and ip
        UDPServerSocket.bind((self.ServerIp, self.BroadcastUdpPort))
        print(f'Server started, listening on IP address {self.ServerIp}')

        # print("in   ", time.time())

        # Send offers
        offersThread = Thread(target=self.sendOffers, args=(UDPServerSocket,))
        offersThread.start()

        # Listen for incoming datagrams
        replyThread = Thread(target=self.replyToMessages, args=(time.time() + 10,))
        replyThread.start()

        # Wait for at most 10 seconds for the thread to complete.
        offersThread.join()
        replyThread.join()
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
                # print("out sendOffers   ", time.time())
                break

    def replyToMessages(self, my_time=time.time()):
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
                sSocket.settimeout(10)

                # binding socket
                # s.bind((socket.gethostname(), self.TcpPort))
                sSocket.bind(('0.0.0.0', self.TcpPort))
                sSocket.listen(1)

                # connecting clients
                clientsocket, address = sSocket.accept()
                # clientsocket.setblocking(10)

                clientName = clientsocket.recv(1024).decode("utf-8")

                self.clients[address] = (clientsocket, clientName)
                # self.clients[address] = clientsocket  # dict contains: (ip,port)->TCP connection
                sSocket.setblocking(True)  # prevents timeout

                # data = clientsocket.recvfrom(self.bufferSize) # i dont send nothing no more

            except socket.timeout:  # todo check if to erase the type of the e - socket.timeout
                print('time out reached: ', time.time() - my_time)  # todo delete that print
                stopped = True

        # print("out replyToMessages   ", time.time())

    def handleStartGame(self):
        msg = f'Welcome to Keyboard Spamming Battle Royale.\n' \
              f'Group 1:\n' \
              f'==\n' \
              f'{self.printGroup1()}\n' \
              f'Group 2:\n' \
              f'==\n' \
              f'{self.printGroup2()}\n'
        self.handleGameAnnouncements(msg)

        p = Pool()
        # results = p.map(self.handleGameThread(),self.clients.items())  # results - tup of the counted keyboard preses
        flag1, flag2 = False, False
        timeoutOfGame = time.time() + 10
        for addr, (conn, name) in self.clients.items():
            if addr in self.group1.keys():
                flag1 = True
                handleGameThread_1 = Thread(target=self.handleGameThread_1, args=(addr, conn, name, timeoutOfGame))
                handleGameThread_1.start()
            if addr in self.group2.keys():
                flag2 = True
                handleGameThread_2 = Thread(target=self.handleGameThread_2, args=(addr, conn, name, timeoutOfGame))
                handleGameThread_2.start()
        if flag1:
            handleGameThread_1.join()
        if flag2:
            handleGameThread_2.join()

        Score1 = sum(self.scoreGroup1.values())
        Score2 = sum(self.scoreGroup2.values())
        msg = f'Game Over!\nGroup 1 typed in {Score1} characters. Group 2 typed in {Score2} characters.\n'
        if Score2 > Score1:
            msg += 'Group 2 wins!'
            winG = self.printGroup2()
        if Score2 < Score1:
            msg += 'Group 1 wins!'
            winG = self.printGroup1()
        else:
            msg += 'It\'s a tie!'
        msg += "Congratulations to the winners:\n==\n" + winG

        self.handleGameAnnouncements(msg)
        print("Score1: ", Score1, " Score2: ", Score2)

    def handleGameThread_1(self, addr, conn, name, timeOutOfGame):
        count = 0
        while time.time() < timeOutOfGame:
            char = conn.recv(1024)
            # print(char)
            if len(char) > 0:
                count += 1
            else:
                print('liraz right')
        self.scoreGroup1[addr] = count
        print(f"addr: {addr}, name: {name}, count of press: {count}")

    def handleGameThread_2(self, addr, conn, name, timeOutOfGame):
        count = 0
        while time.time() < timeOutOfGame:
            char = conn.recv(1024).decode('utf-8')
            if len(char) > 0:
                count += 1
            else:
                print('liraz right')
        self.scoreGroup2[addr] = count
        print(f"addr: {addr}, name: {name}, count of press: {count}")

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

    # def handleGameAnnouncement(self):
    #     for i, tup in enumerate(self.clients.items()):
    #         add, (conn, name) = tup
    #         msg = f'Welcome to Keyboard Spamming Battle Royale.\n' \
    #               f'Group 1:\n' \
    #               f'==\n' \
    #               f'{self.printGroup1()}\n' \
    #               f'Group 2:\n' \
    #               f'==\n' \
    #               f'{self.printGroup2()}\n'
    #         conn.send(bytes(msg, 'utf-8'))

    def handleGameAnnouncements(self,msg):
        for i, tup in enumerate(self.clients.items()):
            add, (conn, name) = tup
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
                self.clients = {}
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
    while True:
        server.createUDPSocket()
        # print("\nClients ->", server.clients)
        server.handleGroupsDividing()
        # print("\ngroup 1 ->", server.group1)
        # print("\ngroup 2 ->", server.group2)
        # print()
        # server.handleGameAnnouncement()
        if len(server.clients.keys()) > 0:
            server.handleStartGame()
        else:
            break
