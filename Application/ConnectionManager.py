import socket
import threading


class ConnectionManager:
    def __init__(self, bind_ip="0.0.0.0", bind_port=9999, socket_type=socket.SOCK_STREAM):
        self.bind_ip   = bind_ip
        self.bind_port = bind_port
        self.socket    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_handler = None
    #

    def start_server(self, backlog_conns=5, type_conns=socket.SOCK_STREAM):
        def handle_client(client_socket):
            # this is client-handling function thread
            request = client_socket.recv(1024)

            print("[*] Received: %s" % request.decode())

            # send back a packet
            client_socket.send(b"ACK!")
            client_socket.close()
        #

        # Start the server on specific IP and port listening on
        self.socket.bind((self.bind_ip, self.bind_port))

        # Server start listening with a max backlog of connections set to 5
        self.socketlisten(backlog_conns)

        # print trace
        print("[*] Listening on %s:%d" % (self.bind_ip, self.bind_port))

        while True:
            # when a client connects, we receive the client socket
            # into a client variable, and connection details into addr
            client, addr = self.socket.accept()

            print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

            # spin up our client thread to handle incoming data
            self.client_handler = threading.Thread(target=handle_client, args=(client,))

            # start the thread
            self.client_handler.start()
    #

    def start_client(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect the client
        self.socket.connect((self.bind_ip, self.bind_port))

        # send some data
        self.socket.send(b"How are you?")
        # client.sendto(b"AAABBBCCC", (target, tport))

        # receive response
        # response = client.recv(4096)
        response, addr = self.socket.recvfrom(4096)

        print(response)
#