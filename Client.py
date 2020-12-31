import socket
import struct
import time

# :*********** For Running on Windows ************:
# from pynput import keyboard


# :*********** For Running on Linux ************:
import sys
import termios
import tty


class Client:
    def __init__(self, teamName):
        self.clientIP = socket.gethostbyname(socket.gethostname())
        self.clientUdpPort = 13117
        self.teamName = teamName
        self.bufferSize = 1024
        self.serverIP = None
        self.serverPort = None
        self.tcpSocket = None
        self.msg = 'Client started, listening for offer requests...'
        self.UDPClientSocket = None

    def LookForServer(self):
        """

        :return: the client is listening to port 13117, waiting to get a *valid offer* from a server.

        """

        # Create a UDP socket at client side
        print(self.msg)
        while True:
            self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.UDPClientSocket.settimeout(10)
            self.UDPClientSocket.bind(('', self.clientUdpPort))

            try:
                offer, (self.serverIP, server_port) = self.UDPClientSocket.recvfrom(
                    self.bufferSize)  # example of the accepted packet: (b'\xef\xbe\xed\xfe\x02\x00P\xc3', ('192.168.56.1', 13117))

                try:
                    offer = struct.unpack('IbH', offer)
                except struct.error:
                    offer = struct.unpack('Ibh!', offer)

                if (offer[0], offer[1]) == (4276993775, 2):  # check if th offer is valid.
                    self.serverPort = offer[2]
                    print(f'Received offer from {self.serverIP}, attempting to connect...')
                    self.createTcpConnection()
                    break
            except socket.timeout:  # todo delete the except
                pass  # the client will keep running, as requested in the Guidelines

    def createTcpConnection(self):
        """

        :return: after the client accepted a valid offer from a server, it will send a request for tcp-connection.
                then, waits for the server to accept the connection, start playing and finally waits for the messages and prints them on the screen.
        """

        # sends the request for tcp-connection:
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.connect((self.serverIP, self.serverPort))
        self.tcpSocket.send(bytes(f'{self.teamName}', 'utf-8'))

        # wait for the server's response
        try:
            msg = self.tcpSocket.recv(1024)
            msg = msg.decode("utf-8")
            if len(msg) > 0:
                print(msg)

        except socket.timeout:
            self.tcpSocket.close()

        # start playing:
        self.startPlaying(self.tcpSocket)

        # waiting for the game summary message and prints it to the screen:
        while True:
            try:
                msg = self.tcpSocket.recv(self.bufferSize)
                msg = msg.decode("utf-8")
                if len(msg) > 0:
                    print(msg)
                    break

            except OSError:
                pass

        # self.tcpSocket.close()

        self.msg = 'Server disconnected, listening for offer requests...'

        # check if the tcp_connection aborted:
        try:
            while True:
                self.tcpSocket.send(bytes('check', 'utf-8'))
        except ConnectionAbortedError:

            # if the connection is aborted, close the socket and rerun the client!
            self.msg = 'Server disconnected, listening for offer requests...'
            self.tcpSocket.close()
            self.UDPClientSocket.close()
            self.LookForServer()

    # :*********** For Running on Windows ************:
    # def startPlaying(self, socket_tcp):
    #     """
    #
    #     :param socket_tcp: the existing tcp_connection socket.
    #     :return: this function is responsible for sending the keys that are being pressed through the connection to the server.
    #     """
    #     # set timeout for the client (the server is not accepting anymore key-presses after 10 second either way, but if the client keep sending keys he will some ugly prints in his terminal)
    #     timeout = time.time() + 10
    #
    #     # we call this function every time a keypress-event is occurs and handling it(send the key - {'a'/'b' ... } to the server).
    #     def on_press(key):
    #         """
    #
    #         :param key: the key pressed
    #         :return: sends the key to the server
    #         """
    #         try:
    #             if time.time() > timeout:
    #                 return False
    #             socket_tcp.send(bytes(str(key), 'utf-8'))
    #         except ConnectionAbortedError:
    #             self.bufferSize = 1024
    #             print('', end='')
    #             return False
    #
    #     # we call this function every time a key-released event occurs(not interesting us).
    #     def on_release(key):
    #         """
    #
    #         :param key: the key released
    #         :return: dont need to do something
    #         """
    #         pass
    #
    #     listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    #     listener.start()
    #     listener.join()

    # :*********** For Running on Linux (SSH) ************:
    def startPlaying(self, socket_tcp):
        timeout = time.time() + 10
        orig_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
        x = 0
        while time.time() < timeout:
            x = sys.stdin.read(1)[0]
            socket_tcp.send(bytes(str(x), 'utf-8'))

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)


if __name__ == '__main__':
    client = Client("QueenGambit")
    client.LookForServer()
