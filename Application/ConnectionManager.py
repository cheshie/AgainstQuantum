import socket
import threading
import curses
from time import sleep
import struct
import json


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

        self.read_handler  = None
        self.write_handler = None
        self.remote    = self.RemoteAPI(self.socket, self.ip, self.port)
    #

    def start_server(self, chatref, backlog_conns=5, type_conns=socket.SOCK_STREAM):
        # self.chat_handler = threading.Thread(target=display_chat, args=('server',))
        # self.chat_handler.start()

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

            # print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

            message = self.handle_user_request(client)
            message_decoded = json.loads(message)
            chatref.display_message_main(message_decoded)
            client.close()

            # Send the response back
            # client.sendall(struct.pack("<I", len(message)))
            # client.sendall(message.encode())
            # client.close()

            # Handle reading responses and answering
            # self.read_handler = threading.Thread(target=self.read_response, args=(client,))
            # self.write_handler = threading.Thread(target=self.write_response, args=(client,))

            # self.read_handler.start(); self.write_handler.start()
    #

    def start_client(self, message):
        # self.chat = ChatManager('client')

        # self.socket.connect((self.ip, self.port))

        self.remote.send_message(message)

        # Should validate connection! somehow!
        # print("[*] Started connection with: ", self.ip + ":" + str(self.port))
        # print("[*] Press [CTRL + C] to exit.")

        # Handle reading responses and answering
        # self.read_handler = threading.Thread(target=self.read_response, args=(self.socket,))
        # self.write_handler = threading.Thread(target=self.write_response, args=(self.socket,))
        # self.read_handler.start(); self.write_handler.start()
        # response = client.recv(4096)

        # try:

        # except KeyboardInterrupt:
        #     print("[!] Connection ended.")
        #     self.socket.close()
    #

    def handle_user_request(self, client):
        # Get length of structure containing function information
        # Up to 4 bytes - could be shorter
        data = client.recv(4)

        # Client did not send valid value
        if not data:
            client.close()
            return

        # Get the structure from client
        data_len = struct.unpack("<I", data)[0]
        data = client.recv(data_len)

        # Client did not send the strcutre
        if not data:
            client.close()
            return

        loaded_data = json.loads(data)
        # print(loaded_data)

        # Interpret sent structure into function
        remote_name = loaded_data['func']
        remote_args = tuple(loaded_data['argv'])

        # Determine if server supports this function
        if remote_name not in self.remote.shared:
            print("[!] Server does not support that function.")
            client.close()
            return

        # Get valid function from server
        func = self.remote.shared[remote_name]

        # Check arguments passed for the function
        for arg_type, remote_arg in zip(func['argv'], remote_args):
            if type(remote_arg) is not arg_type:
                # print("Incorrect argument type: ",arg_type, type(remote_arg))
                client.close()
                return

        return json.dumps(func['f'](*remote_args))
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
    #

    def write_response(self, cl_soc):
        while True: self.send_message(recipient=cl_soc)
    #

    def read_response(self, cl_soc):
        while True: self.receive_message(cl_soc)
    #

    class RemoteAPI:
        def __init__(self, socket, ip, port):
            self.socket = socket
            self.ip = ip
            self.port = port
            self.shared = {
            'send_message': { 'argv': [dict], 'f': self.rpc_send_message}}
        #

        def connect(self):
            self.socket.connect((self.ip, self.port))
        #

        def disconnect(self):
            self.socket.close()
        #

        def __getattr__(self, name):
            def worker(*args):
                self.connect()

                # Get function skeleton
                fun_info = json.dumps({'func': name, 'argv': list(args)})

                # Send that structure to server
                self.socket.sendall(struct.pack("<I", len(fun_info)))
                self.socket.sendall(fun_info.encode())

                # Get initial response from server
                data = self.socket.recv(4)

                # Server not responding
                if not data:
                    self.disconnect()
                    return

                # Receive back value returned by function
                data_len = struct.unpack('<I', data)[0]
                data = self.socket.recv(data_len)

                # If server responded return received data
                if data:
                    return json.loads(data)

                self.disconnect()

            return worker
        #

        def rpc_send_message(self, message):
            return message
        #
    #
#