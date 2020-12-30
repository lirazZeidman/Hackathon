import socket
import struct
import keyboard
import time
from StopableThread import StoppableThread


class Client:
    def __init__(self, teamName):
        self.clientIP = socket.gethostbyname(socket.gethostname())
        self.clientUdpPort = 13117
        self.teamName = teamName
        self.bufferSize = 1024
        self.serverIP = None
        self.serverPort = None
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print('Client started, listening for offer requests...')

        msgFromClient = "Hello UDP Server"
        self.bytesToSend = str.encode(msgFromClient)

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
                    self.createTcpConnection()
                    break
            except socket.timeout:  # todo delete the except
                pass
                # print('timeout reached, LookForServer')

    def createTcpConnection(self):
        # self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpSocket.connect((self.serverIP, self.serverPort))
        self.tcpSocket.send(bytes(f'{self.teamName}', 'utf-8'))
        try:
            msg = self.tcpSocket.recv(1024)
            msg = msg.decode("utf-8")
            if len(msg) > 0:
                print(msg)

        except socket.timeout:
            self.tcpSocket.close()

        print("time to start the big game!")
        self.startPlaying()

        # gamingThread = StoppableThread(target=self.gaming, args=(s,))
        # gamingThread.start()

        # Thread.Timer(10, self.LookForServer).start()
        # gamingThread.join(10)

        # if gamingThread.is_alive():
        #     gamingThread.stop()
        # if gameingThread.is_alive():
        #     gameingThread.set()
        print("the big  ended!")

        try:
            msg = self.tcpSocket.recv(1024)
            msg = msg.decode("utf-8")
            if len(msg) > 0:
                print(msg)

        except OSError:
            pass

        self.tcpSocket.close()
        self.LookForServer()

    def startPlaying(self):
        def send_pressed_keys(e):
            self.tcpSocket.send(bytes(str(e), 'utf-8'))

        while self.tcpSocket:
            keyboard.on_press(send_pressed_keys)
            keyboard.wait()

        try:
            msg = self.tcpSocket.recv(1024)
            msg = msg.decode("utf-8")
            if len(msg) > 0:
                print(msg)

        except OSError:
            pass


if __name__ == '__main__':
    client = Client("Rob0tSoF1A")
    client.LookForServer()
