import socket
import threading
import curses
from time import sleep


class ConnectionManager:
    def __init__(self, ip="0.0.0.0", port=9999, socket_type=socket.SOCK_STREAM):
        self.client_handler = None
        self.socket = socket.socket(socket.AF_INET, socket_type)
        self.ip   = ip
        self.port = port

        self.me_name  = "ME"
        self.you_name = "YOU"
        self.prompt   = "?>"
        self.server_conns = []

        self.read_handler = None
        self.write_handler = None
    #

    def start_server(self, backlog_conns=5, type_conns=socket.SOCK_STREAM):
        # Start the server on specific IP and port listening on
        self.socket.bind((self.ip, self.port))

        # Server start listening with a max backlog of connections set to 5
        self.socket.listen(backlog_conns)

        # print trace
        # print("[INFO] Listening on %s:%d" % (self.ip, self.port))

        # server loop - handling incoming connections
        while True:
            client, addr = self.socket.accept()
            self.server_conns += client, addr
            print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

            # Handle reading responses and answering
            self.read_handler = threading.Thread(target=self.read_response, args=(client,))
            self.write_handler = threading.Thread(target=self.write_response, args=(client,))

            self.read_handler.start(); self.write_handler.start()
    #

    def start_client(self):
        self.socket.connect((self.ip, self.port))

        # Should validate connection! somehow!
        print("[*] Started connection with: ", self.ip + ":" + self.port)

        # Handle reading responses and answering
        self.read_handler = threading.Thread(target=self.read_response, args=(self.socket,))
        self.write_handler = threading.Thread(target=self.write_response, args=(self.socket,))
        self.read_handler.start(); self.write_handler.start()
        # response = client.recv(4096)

        try:
            while True:
                sleep(0.1)
        except KeyboardInterrupt:
            print("[!] Connection ended. ")
            self.socket.close()
    #

    def send_message(self, message=None, recipient=None):
        # Prompt user for message
        if message is None:
            message = input(self.me_name + " " + self.prompt + " ")

        if recipient is None:
            recipient = self.socket

        recipient.send(str.encode(message))
    #

    def receive_message(self, client=None, size_bytes=1024):
        if client is None:
            client = self.socket

        request = client.recv(size_bytes)
        print("\n" + self.you_name + " " + self.prompt + " " + request.decode())

    def write_response(self, cl_soc):
        while True: self.send_message(recipient=cl_soc)

    def read_response(self, cl_soc):
        while True: self.receive_message(cl_soc)
#