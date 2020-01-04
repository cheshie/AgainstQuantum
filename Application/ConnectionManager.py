import socket
import threading
import struct
import json
import random
from time import sleep
from datetime import datetime
# TODO: ANNOTATIONS

class ConnectionManager:
    def __init__(self, ip="0.0.0.0", port=9999, client_port=9777, client_ip='0.0.0.0',
                 socket_type=socket.SOCK_STREAM, mode='visual'):
        # For both server and client
        self.socket = socket.socket(socket.AF_INET, socket_type)

        # For server - it will listen on this pair
        # For client - it will connect using this pair
        self.ip   = ip
        self.port = port

        # Client will listen on this port and addr for any messages sent to
        # The server by other users
        self.client_ip = client_ip
        self.client_port = client_port

        # Maintain a list of all connections to the server (list of sockets, list of IPs, list of ports)
        self.server_conns = (list(), list(), list())
        self.mode = mode

        # Class that brings RPC capability, default success response for its functions
        self.remote = self.RemoteAPI(self.ip, self.port)
        self.success = json.dumps({'code': 200}).encode()
    #

    def start_server(self, chatref, backlog_conns=5):
        # Start the server on specific IP and port listening on
        self.socket.bind((self.ip, self.port))

        # Server start listening with a max backlog of connections set to 5
        self.socket.listen(backlog_conns)

        self.log("[*] Listening on %s:%d" % (self.ip, self.port))

        while True:
            # Accept connection and add to list of connections
            client, addr = self.socket.accept()
            self.log("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

            # Get user message, send it to all clients, optionally display
            message = self.handle_user_request(client)
            sender = self.add_server_conn(client, addr, message['port'])
            self.log(f"[*] New sender added: {sender[1]}:{sender[2]}")
            self.broadcast_message(message, sender)
            if self.mode == 'visual':
                chatref.display_message_main(message)
    #

    def start_client(self, chatref):
        # start listening for any message broadcast by the server
        self.answer_listener = threading.Thread(target=self.wait_for_response, args=(chatref, ))
        self.answer_listener.start()
    #

    # Client will wait for any messages send by the server
    def wait_for_response(self, chatref):
        # Wait for other threads
        sleep(0.1)

        # Bind new socket on specified port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Try to connect on default port - it does only check once if port is occupied
        # If it finds port already in use on second time - program will throw exception
        try:
            self.client_socket.bind((self.client_ip, self.client_port))
        except OSError:
            newport = random.randint(self.client_port, 2 * self.client_port)
            self.client_socket.bind((self.client_ip, newport))
            self.client_port = newport
            self.log(f"[!] Failed to create client listener on chosen port. This port was used instead: {newport}")

        self.client_socket.listen(1)
        self.log("[*] Listening for messages from server on %s:%d" % (self.client_ip, self.client_port))

        while True:
            con, add = self.client_socket.accept()
            # Receive information about size of message sent by the server
            # and then receive and display the message
            size = struct.unpack('<I', con.recv(4))[0]
            chatref.display_message_main(json.loads(con.recv(size).decode()), reset=True)
            con.close()
    #

    def send_message(self, message):
        message['port'] = self.client_port
        response = self.remote.send_message(message)
        self.log(f"[*] Sending message returned: {response.decode()}")
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

        # Client did not send the structure
        if not data:
            client.close()
            return

        # Interpret sent structure into function
        remote_name = json.loads(data)['func']
        remote_args = tuple(json.loads(data)['argv'])

        # Determine if server supports this function
        if remote_name not in self.remote.shared:
            self.log("[!] Server does not support that function.")
            client.close()
            return

        # Get valid function from server
        func = self.remote.shared[remote_name]

        # Check arguments passed for the function
        for arg_type, remote_arg in zip(func['argv'], remote_args):
            if type(remote_arg) is not arg_type:
                self.log(f"[!] Incorrect argument type: {arg_type} {type(remote_arg)}")
                client.close()
                return

        # If reach this point, inform user that function succeeded and return its value
        client.sendall(struct.pack("<I", len(self.success)))
        client.sendall(self.success)
        return func['f'](*remote_args)
    #

    # Add new incoming connection to server list of connections
    def add_server_conn(self, client, addr, port):
        # Check if client IP (addr[0]) is not already in the list
        if addr[0] not in self.server_conns[1] or port not in self.server_conns[2]:
            # If not - add socket and IP
            self.server_conns[0].append(client)
            self.server_conns[1].append(addr[0])
            self.server_conns[2].append(port)

        return (client, addr[0], port)
    #

    # Broadcast message received by server to all connected clients
    def broadcast_message(self, message, sender):
        # For IP addresses that connected earlier to the server
        for conn in zip(*self.server_conns):
            # Omit sending message back to the sender
            # Compare IP and Port
            if conn[1] == sender[1] and conn[2] == sender[2]:
                continue

            # Send message to all other connected users
            cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cl.connect((conn[1], conn[2]))
            # Send information about size of message and then message
            cl.sendall(struct.pack("<I", len(json.dumps(message).encode())))
            cl.sendall(json.dumps(message).encode())
            self.log(f"[*] Message broadcast to {conn[1]+':'+str(conn[2])}")
            cl.close()
    #

    def log(self, msg):
        if self.mode == 'text':
            print(msg)
        elif self.mode == 'visual':
            logfile = open(datetime.now().strftime("%m-%d-%Y"+".log"), 'a+')
            logfile.write(datetime.now().strftime("%H:%M:%S") + " : " + msg + '\n')
    #

    class RemoteAPI:
        def __init__(self, ip, port):
            self.ip = ip
            self.port = port
            self.shared = {
            'send_message': { 'argv': [dict], 'f': self.rpc_send_message}}
        #

        def connect(self):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                    return data

                self.disconnect()

            return worker
        #

        def rpc_send_message(self, message):
            return message
        #
    #
#