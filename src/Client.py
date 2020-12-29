import socket
import struct
import time


class Client:
    def __init__(self, teamName):
        self.clientIP = socket.gethostbyname(socket.gethostname())
        self.clientUdpPort = 13117
        self.teamName = teamName + '\n'
        self.bufferSize = 1024
        self.serverIP = None
        self.serverPort = None

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
                    self.createTcpConnection(offer)
                    break
            except socket.timeout:
                print('timeout reached, LookForServer')
                break

    def createTcpConnection(self, offer):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)  # TODO: delete this later
        s.connect((self.clientIP, self.serverPort))
        s.send(bytes('motha fucker', 'utf-8'))
        # print('socket.gethostname(): ', socket.gethostname())
        # print('self.serverPort: ', self.serverPort)

        timeout = time.time() + 10
        full_msg = ''
        try:
            while True:
                msg = s.recv(1024)
                if len(msg) <= 0:
                    break
                msg = msg.decode("utf-8")

                if len(msg) > 0:
                    print(msg)

        except socket.timeout:
            print('tcp-connection timeout has reached')
            s.close()
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect((self.serverIP, self.serverPort))
        # msg = struct.pack('IbH', 0xfeedbeef, 0x2, self.serverPort)
        # s.sendall(msg)
        #
        # data = s.recv(1024)
        # print(data.decode('utf-8'))

        # sock.bind(('', self.serverPort))
        # msg = struct.pack('IbH', 0xfeedbeef, 0x2, self.serverPort)
        # dest = ('<broadcast>', self.serverPort)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # print('sends request to tcp connection ')  # Todo: Edit that print
        # sock.sendto(msg, dest)

        # print('message accepted: ', msg)
        # self.clientIP = self.clientIP  # todo delete that non sense
        # print('creating tcp connection')

        # # TODO: please dont die
        # message, address = sock.recvfrom(self.bufferSize)
        # print('message: ', message)
        # print('address: ', address)
        #
        # connection, address2 = sock.accept()
        # print('connection: ', connection)
        # print('address2: ', address2)


if __name__ == '__main__':
    client = Client('QueenGambit')
    client.LookForServer()
