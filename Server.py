import socket
import struct
import time
from threading import Thread
from StopableThread import StoppableThread

# :*********** For Running on Linux ************:
from scapy.arch import get_if_addr


class bcolors:
    ResetAll = "\033[0m"

    Bold = "\033[1m"
    Dim = "\033[2m"
    Underlined = "\033[4m"
    Blink = "\033[5m"
    Reverse = "\033[7m"
    Hidden = "\033[8m"

    ResetBold = "\033[21m"
    ResetDim = "\033[22m"
    ResetUnderlined = "\033[24m"
    ResetBlink = "\033[25m"
    ResetReverse = "\033[27m"
    ResetHidden = "\033[28m"

    Default = "\033[39m"
    Black = "\033[30m"
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Magenta = "\033[35m"
    Cyan = "\033[36m"
    LightGray = "\033[37m"
    DarkGray = "\033[90m"
    LightRed = "\033[91m"
    LightGreen = "\033[92m"
    LightYellow = "\033[93m"
    LightBlue = "\033[94m"
    LightMagenta = "\033[95m"
    LightCyan = "\033[96m"
    White = "\033[97m"

    BackgroundDefault = "\033[49m"
    BackgroundBlack = "\033[40m"
    BackgroundRed = "\033[41m"
    BackgroundGreen = "\033[42m"
    BackgroundYellow = "\033[43m"
    BackgroundBlue = "\033[44m"
    BackgroundMagenta = "\033[45m"
    BackgroundCyan = "\033[46m"
    BackgroundLightGray = "\033[47m"
    BackgroundDarkGray = "\033[100m"
    BackgroundLightRed = "\033[101m"
    BackgroundLightGreen = "\033[102m"
    BackgroundLightYellow = "\033[103m"
    BackgroundLightBlue = "\033[104m"
    BackgroundLightMagenta = "\033[105m"
    BackgroundLightCyan = "\033[106m"
    BackgroundWhite = "\033[107m"


class Server:

    def __init__(self):
        # self.ServerIp = socket.gethostbyname(socket.gethostname())
        self.ServerIp = '127.0.0.1'
        # self.ServerIp = get_if_addr('eth1')
        self.BroadcastUdpPort = 13117
        self.TcpPort = 50000
        self.bufferSize = 1024
        self.msg = f'{bcolors.Cyan}Server started, listening on IP address {self.ServerIp}{bcolors.ResetAll}'
        self.UDPServerSocket = None

        self.clients = {}
        self.group1 = {}
        self.group2 = {}

        self.scoreGroup1 = {}
        self.scoreGroup2 = {}

    def createUDPSocket(self):
        """
        this function is responsible for sending offers and accepting tcp-requests from the clients (through threads).
        """

        # Create a datagram(UDP) socket
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Bind to address and ip
        self.UDPServerSocket.bind((self.ServerIp, self.BroadcastUdpPort))
        self.UDPServerSocket.settimeout(10)

        # prints the starting message (you can check in the init)
        print(self.msg)

        # Send offers - thread
        offersThread = Thread(target=self.sendOffers, args=(self.UDPServerSocket,))
        offersThread.start()

        # Listen for incoming packet - replying messages thread
        replyThread = Thread(target=self.replyToMessages, args=(time.time() + 10,))
        replyThread.start()

        # Wait for at most 10 seconds for the thread to complete.
        offersThread.join(10)
        replyThread.join(10)

    def sendOffers(self, UDPServerSocket):
        """
        through the UDPServerSocket the server sends broadcast messages with the requested format.
        :param UDPServerSocket: the udp socket
        """

        # send 10 broadcasts, 1 every second - 10 seconds in total.
        counter = 0
        while True:
            if counter < 10:
                # as we saw on the ssh connection, other clients tried (at least for us) sending packets with 2 different formats:
                try:
                    msg = struct.pack('Ibh!', 0xfeedbeef, 0x2, self.TcpPort)  # Little-endian (LE)
                except:
                    msg = struct.pack('IbH', 0xfeedbeef, 0x2, self.TcpPort)  # Big-endian (BE)

                dest = ('<broadcast>', self.BroadcastUdpPort)
                UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                UDPServerSocket.sendto(msg, dest)
                counter += 1
                time.sleep(1)

            else:
                break

    def replyToMessages(self, MaxTime):
        """
        this function handles the client tcp-request and accepts them. it stops accepting clients for 2 reason.
        1st is the MaxTime.
        2nd is if the client doesn't send it's team name (which resolves Exception).

        every clients that is being connected, is being added to a dictionary of clients the server holds.

        :param MaxTime: that is the Countdown for the function. when time.time() reaches it, the function will finish running.
        """

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
                sSocket.bind(('0.0.0.0', self.TcpPort))
                sSocket.listen()

                # connecting clients
                clientsocket, address = sSocket.accept()

                clientName = clientsocket.recv(self.bufferSize).decode("utf-8")

                self.clients[address] = (clientsocket, clientName)
                # self.clients[address] = clientsocket  # dict contains: (ip,port)->TCP connection
                sSocket.setblocking(True)  # prevents timeout

                # data = clientsocket.recvfrom(self.bufferSize) # i dont send nothing no more

            except socket.timeout:
                stopped = True

    def handleStartGame(self):
        """
        first of all that function sends all the clients the "Welcome ... " message, which clarifies the Group members.
        then divide the program into 2 threads. each thread handles the messages received from a Group over the tcp connection
        """

        # assemble the welcome message:
        msg = f'{bcolors.Blue}Welcome to Keyboard Spamming Battle Royale.\n{bcolors.ResetAll}' \
              f'{bcolors.Magenta}Group 1:\n' \
              f'==\n' \
              f'{self.printGroup1()}{bcolors.ResetAll}\n' \
              f'{bcolors.Green}Group 2:\n' \
              f'==\n' \
              f'{self.printGroup2()}{bcolors.ResetAll}\n\n' \
              f'{bcolors.Bold}Start pressing keys on your keyboard as fast as you can!!\n{bcolors.ResetAll}'

        # send the @msg to each connected client
        self.handleGameAnnouncements(msg)

        handleGameThread_1 = None
        handleGameThread_2 = None

        timeoutOfGame = time.time() + 10

        # open thread for each client and start listen to packets received:
        for adder, (conn, name) in self.clients.items():

            # if client belongs to group1:
            if adder in self.group1.keys():
                handleGameThread_1 = StoppableThread(target=self.handleGameThread_1,
                                                     args=(adder, conn, timeoutOfGame))
                handleGameThread_1.start()

            # if client belongs to group2:
            if adder in self.group2.keys():
                handleGameThread_2 = StoppableThread(target=self.handleGameThread_2,
                                                     args=(adder, conn, timeoutOfGame))
                handleGameThread_2.start()

        # wait for all the threads to finish.
        time_left = timeoutOfGame - time.time()
        if handleGameThread_1 is not None:
            handleGameThread_1.join(time_left)

        if handleGameThread_2 is not None:
            handleGameThread_2.join(time_left)

        Score1 = sum(self.scoreGroup1.values())
        Score2 = sum(self.scoreGroup2.values())

        # assemble the end game message:
        msg = f'{bcolors.BackgroundLightGreen}{bcolors.DarkGray}{bcolors.Bold}Game Over!\n{bcolors.ResetAll}{bcolors.Magenta}Group 1 typed in {Score1} characters.{bcolors.ResetAll}{bcolors.Green}Group 2 typed in {Score2} characters.\n{bcolors.ResetAll}'
        winG = ""
        if Score2 > Score1:
            msg += f'{bcolors.BackgroundLightCyan}{bcolors.DarkGray}Group 2 wins!\n{bcolors.ResetAll}'
            winG = self.printGroup2()
        if Score2 < Score1:
            msg += f'{bcolors.BackgroundLightCyan}{bcolors.DarkGray}Group 1 wins!\n{bcolors.ResetAll}'
            winG = self.printGroup1()
        else:
            msg += f'{bcolors.BackgroundLightCyan}{bcolors.DarkGray}It\'s a tie!\n{bcolors.ResetAll}'
        msg += "\nCongratulations to the winners:\n==\n" + winG

        # send the @msg to each connected client
        self.handleGameAnnouncements(msg)

        # after the session ended, disconnect from all the clients, and reset all the attributes
        for c in self.clients.values():
            c[0].close()
        self.clients = {}
        self.group1 = {}
        self.group2 = {}
        self.scoreGroup1 = {}
        self.scoreGroup2 = {}

        self.UDPServerSocket.shutdown(socket.SHUT_RDWR)
        self.UDPServerSocket.close()
        self.msg = "Game over, sending out offer requests..."
        # self.createUDPSocket()

    def handleGameThread_1(self, adder, conn, timeToEnd):
        """
        counts the number of keys pressed for each client. update in the attribute self.scoreGroup1
        :param adder: address of the client
        :param conn: socket between the server and the client
        :param timeToEnd: time to live of the thread :)
        """
        conn.setblocking(0)
        self.scoreGroup1[adder] = 0
        while time.time() < timeToEnd:
            try:
                char = conn.recv(self.bufferSize)
                if len(char) > 0:
                    self.scoreGroup1[adder] += 1
            except:
                if time.time() < timeToEnd:
                    continue
                else:
                    break

    def handleGameThread_2(self, adder, conn, timeToEnd):
        """
       counts the number of keys pressed for each client. update in the attribute self.scoreGroup2
       :param adder: address of the client
       :param conn: socket between the server and the client
       :param timeToEnd: time to live of the thread :)
       """
        conn.setblocking(0)
        self.scoreGroup2[adder] = 0
        while time.time() < timeToEnd:
            try:
                char = conn.recv(self.bufferSize)
                if len(char) > 0:
                    self.scoreGroup2[adder] += 1
            except:
                if time.time() < timeToEnd:
                    continue
                else:
                    break

    def printGroup1(self):
        """
        prints the name of all the group members in group 1, in the requested format.
        """
        g1 = ""
        for add, (conn, name) in self.group1.items():
            g1 += str(name) + "\n"
        return g1

    def printGroup2(self):
        """
        prints the name of all the group members in group 2, in the requested format.
        :return:
        """
        g2 = ""
        for add, (conn, name) in self.group2.items():
            g2 += str(name) + "\n"
        return g2

    def handleGroupsDividing(self):
        """
        divides the clients into 2 Groups of players. if the number of players is odd then group 1 will have the extra player.
        """
        for i, tup in enumerate(self.clients.items()):
            add, (conn, name) = tup
            if len(self.clients) / 2 > i:
                self.group1[add] = (conn, name)
            else:
                self.group2[add] = (conn, name)

    def handleGameAnnouncements(self, msg):
        """
        sends the msg to all the connected members.
        :param msg: msg to send
        """
        for i, tup in enumerate(self.clients.items()):
            add, (conn, name) = tup
            conn.send(bytes(msg, 'utf-8'))

    def runServer(self):
        """
        responsible for running the server in a loop!
        """

        while True:
            self.createUDPSocket()
            self.handleGroupsDividing()
            if len(self.clients.keys()) > 0:
                self.handleStartGame()


if __name__ == '__main__':
    server = Server()
    server.runServer()
