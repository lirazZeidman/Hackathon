# import socket
#
# HEADERSIZE = 7
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((socket.gethostname(), 1234))
# s.listen(5)  # size of queue = 200
#
# while True:
#     # now our endpoint knows about the OTHER endpoint.
#     clientsocket = None
#     while clientsocket is None:
#         clientsocket, address = s.accept()
#         if clientsocket is None:
#             time.sleep(1)
#         else:
#             print(f"Connection from {address} has been established.")
#
#     msg = "Welcome to the server!"
#     msg = f'{len(msg):<{HEADERSIZE}}' + msg
#
#     clientsocket.send(bytes(msg, "utf-8"))
#     # clientsocket.close()

#
# import socket
# import msvcrt
# import select
# import time
#
# HEADERSIZE = 7
#
# IP="123.0.0.1"
# Prot=1234
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((socket.gethostname(), 1241))
# s.listen(5)  # size of queue = 5
#
# print(f"Server started, listening on IP address {socket.gethostbyname(socket.gethostname())}.")
#
# while True:
#     # now our endpoint knows about the OTHER endpoint.
#     clientsocket, address = s.accept()  # address is equal to: (dest-ip, dest-port)
#     print(f"Connection from {address} has been established.")
#
#     msg = f"{socket.gethostbyname(socket.gethostname())}"
#     # msg = f"{len(msg):<{HEADERSIZE}}" + msg
#     clientsocket.send(bytes(msg,'utf-8'))
#
#     if msvcrt.kbhit() and msvcrt.getch() == chr(27):
#         clientsocket.close()
#         break
#     # while True:
#     # msg = f"the time is: {time.time()}"
#     # msg = f"{len(msg):<{HEADERSIZE}}" + msg
#     # clientsocket.send(bytes(msg, "utf-8"))
#     # time.sleep(5)


# ********************************************************************************************
import socket
import msvcrt
import select
import time

HEADERSIZE = 7

IP = socket.gethostname()
Port = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, Port))
server_socket.listen(5)  # size of queue = 5

sockets_list = [server_socket]
Clients = {}


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADERSIZE)  # HEADERSIZE
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False


print(f"Server started, listening on IP address {socket.gethostbyname(socket.gethostname())}.")

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)

            Clients[client_socket] = user

            print(
                f"Accepted new info from {client_address[0]}:{client_address[1]} user name : {user['data'].decode('utf-8')}")

        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(Clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del Clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = Clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Iterate over connected clients and broadcast message
            for client_socket in Clients:

                # But don't sent it to sender
                if client_socket != notified_socket:
                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            # It's not really necessary to have this, but will handle some socket exceptions just in case
        for notified_socket in exception_sockets:
            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)

            # Remove from our list of users
            del Clients[notified_socket]

    # # now our endpoint knows about the OTHER endpoint.
    # clientsocket, address = s.accept()  # address is equal to: (dest-ip, dest-port)
    # print(f"Connection from {address} has been established.")
    #
    # msg = f"{socket.gethostbyname(socket.gethostname())}"
    # # msg = f"{len(msg):<{HEADERSIZE}}" + msg
    # clientsocket.send(bytes(msg, 'utf-8'))
    #
    # if msvcrt.kbhit() and msvcrt.getch() == chr(27):
    #     clientsocket.close()
    #     break
    # # while True:
    # # msg = f"the time is: {time.time()}"
    # # msg = f"{len(msg):<{HEADERSIZE}}" + msg
    # # clientsocket.send(bytes(msg, "utf-8"))
    # # time.sleep(5)
