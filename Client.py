import socket
import struct
import time

# :*********** For Running on Windows ************:
from pynput import keyboard

# :*********** For Running on Linux ************:
# import sys
# import termios
# import tty



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

        # Create a UDP socket at client side
        print(self.msg)
        while True:
            self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.UDPClientSocket.settimeout(10)
            self.UDPClientSocket.bind(('', self.clientUdpPort))

            try:
                offer, (self.serverIP, server_port) = self.UDPClientSocket.recvfrom(self.bufferSize)
                # (b'\xef\xbe\xed\xfe\x02\x00P\xc3', ('192.168.56.1', 13117))
                try:
                    offer = struct.unpack('IbH', offer)
                except struct.error:
                    offer = struct.unpack('Ibh!', offer)


                if (offer[0], offer[1]) == (4276993775, 2):
                    self.serverPort = offer[2]
                    print(f'Received offer from {self.serverIP}, attempting to connect...')
                    self.createTcpConnection()
                    break
            except socket.timeout:  # todo delete the except
                pass
                # print('timeout reached, LookForServer')

    def createTcpConnection(self):
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.connect((self.serverIP, self.serverPort))
        self.tcpSocket.send(bytes(f'{self.teamName}', 'utf-8'))

        try:
            msg = self.tcpSocket.recv(1024)
            msg = msg.decode("utf-8")
            if len(msg) > 0:
                print(msg)

        except socket.timeout:
            self.tcpSocket.close()

        self.startPlaying(self.tcpSocket)
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

        try:
            while True:
                self.tcpSocket.send(bytes('check', 'utf-8'))
        except ConnectionAbortedError:
            self.msg = 'Server disconnected, listening for offer requests...'
            self.tcpSocket.close()
            self.UDPClientSocket.close()
            self.LookForServer()

    # :*********** For Running on Windows ************:
    def startPlaying(self, socket_tcp):
        timeout = time.time() + 10

        def on_press(key):
            try:
                if time.time() > timeout:
                    return False
                socket_tcp.send(bytes(str(key), 'utf-8'))
            except ConnectionAbortedError:
                self.bufferSize = 1024
                print('', end='')
                return False

        def on_release(key):
            pass

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        listener.join()

    # :*********** For Running on Linux ************:
    # def startPlaying(self, socket_tcp):
    #     timeout = time.time() + 10
    #     orig_settings = termios.tcgetattr(sys.stdin)
    #     tty.setcbreak(sys.stdin)
    #     x = 0
    #     while time.time() < timeout:
    #         x = sys.stdin.read(1)[0]
    #         socket_tcp.send(bytes(str(x), 'utf-8'))
    #
    #     termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)


if __name__ == '__main__':
    client = Client("QueenGambit")
    client.LookForServer()
