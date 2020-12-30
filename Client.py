import socket
import struct
global stopFunction



class Client:
    def __init__(self, teamName):
        self.clientIP = socket.gethostbyname(socket.gethostname())
        self.clientUdpPort = 13117
        self.teamName = teamName
        self.bufferSize = 1024
        self.serverIP = None
        self.serverPort = None
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msg = 'Client started, listening for offer requests...'

    def LookForServer(self):

        # Create a UDP socket at client side
        print(self.msg)
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
        print("the big  ended!")
        while True:
            try:
                msg = self.tcpSocket.recv(1024)
                msg = msg.decode("utf-8")
                if len(msg) > 0:
                    print(msg)
                    break

            except OSError:
                pass

        # self.tcpSocket.close()
        try:
            self.tcpSocket.send(bytes('check', 'utf-8'))
        except:
            self.msg = 'Server disconnected, listening for offer requests...'
            global stopFunction
            stopFunction = False
            self.LookForServer()

    def startPlaying(self):
        global stopFunction
        stopFunction = False

        def send_pressed_keys(e):
            global stopFunction
            try:
                self.tcpSocket.send(bytes(str(e), 'utf-8'))
            except ConnectionAbortedError:

                stopFunction = True

        keyboard.on_press(send_pressed_keys)
        if not stopFunction:
            keyboard.wait()


if __name__ == '__main__':
    client = Client("QueenGambit")
    client.LookForServer()
