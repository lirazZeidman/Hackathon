import socket

HEADERSIZE = 7

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Client started, listening for offer requests...')
s.connect((socket.gethostname(), 1241))

while True:
    full_msg = ''
    new_msg = True
    while True:
        msg = s.recv(100)
        if new_msg:
            # print("new msg len:", msg[:HEADERSIZE])
            # print(f"Received offer from {}, attempting to connect...")
            # msglen = int(msg[:HEADERSIZE])
            new_msg = False

        # print(f"full message length: {msglen}")

        # full_msg += msg.decode("utf-8")

        # print(len(full_msg))

        # if len(full_msg) - HEADERSIZE == msglen:

        print(f"Received offer from {msg.decode('utf-8')}, attempting to connect...")
        # print(full_msg[HEADERSIZE:])
        new_msg = True
        # full_msg = ''
    if msvcrt.kbhit() and msvcrt.getch() == chr(27):
        exit()
