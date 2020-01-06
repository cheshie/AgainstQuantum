import socket
import threading
import struct
import json
import random
from time import sleep
from datetime import datetime
from FrodoKEM.frodo640.api_frodo640 import FrodoAPI640 as FrodoAPI
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

        # self.Frodo = FrodoAPI()
        # print("frodoAPI: ", self.Frodo)
        # self.server_pk, self.server_sk = self.Frodo.crypto_kem_keypair_frodo640()
        # open('server_pk.key', 'wb').write(bytearray(self.server_pk))
        # print("saved to file")
        # maybe frodoapi1 api2????

        # For public key exchange
        self.FrodoAPI1 = FrodoAPI()
        self.FrodoAPI2 = FrodoAPI()
        #
        # self.FrodoAPI.set_secret_key(list(open('server_sk.key', 'rb').read()))
        # open('server_sk.key', 'wb').write(bytearray(self.server_pk))

        # # Generating keys - TODO: log generating keys
        self.server_pk, self.server_sk = self.FrodoAPI1.crypto_kem_keypair_frodo640()
        #
        open('server_pk.key', 'wb').write(bytearray(self.server_pk))
        #
        # # CLIENT
        self.FrodoAPI2.set_public_key(list(open('server_pk.key', 'rb').read()))
        c, ss = self.FrodoAPI2.crypto_kem_enc_frodo640()
        open('server_c.key', 'wb').write(bytearray(c))
        print('client ss: ', ss)
        # #
        # #
        # # SERVER
        self.FrodoAPI1.set_ciphertext(list(open('server_c.key', 'rb').read()))
        ss1 = self.FrodoAPI1.crypto_kem_dec_frodo640()
        print('server ss: ', ss1)
        exit(-1)




        # self.FrodoAPI.set_public_key(list(open('server_pk.key', 'rb').read()))
        # self.FrodoAPI.set_secret_key(list(open('server_sk.key', 'rb').read()))
        # c, ss = FrodoAPI.crypto_kem_enc_frodo640()
        # print('ss: ', ss)
        #
        # self.FrodoAPI.set_public_key(list(open('server_pk.key', 'rb').read()))
        # self.FrodoAPI.set_secret_key(list(open('server_sk.key', 'rb').read()))
        # c, ss = FrodoAPI.crypto_kem_enc_frodo640()
        # print('ss: ', ss)
        #
        # self.FrodoAPI.set_public_key(list(open('server_pk.key', 'rb').read()))
        # self.FrodoAPI.set_secret_key(list(open('server_sk.key', 'rb').read()))
        # c, ss = FrodoAPI.crypto_kem_enc_frodo640()
        # print('ss: ', ss)
        # self.FrodoAPI.set_ciphertext(list(open('server_c.key', 'rb').read()))
        # open('server_c.key', 'wb').write(bytearray(c))
        # ss1 = FrodoAPI.crypto_kem_dec_frodo640()

        # print('ss: ', ss1)
        # exit(-1)
        # print('server ss: ', FrodoKEM.crypto_kem_dec())
        # FrodoAPI.crypto_kem_dec_frodo640()
        # FrodoAPI.crypto_kem_enc_frodo640()
        # self.server_pk = self.pk # This you will send
        # print(self.server_pk)
        # Client gets it, encapsulates it and has ready vector
        # Server decapsulates it and has the same vector
        # What with ct? Is it needed?

        while True:
            # Accept connection and add to list of connections
            client, addr = self.socket.accept()
            self.log("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

            # Get user message, send it to all clients, optionally display
            message = self.handle_user_request(client)

            if message is None:
                # No message was sent. User requested another action (i.e. server's public key)
                continue

            # Adding new connection to the server
            sender = self.add_server_conn(client, addr, message['port'])
            self.log(f"[*] New sender added: {sender[1]}:{sender[2]}")

            # If user sent message broadcast it to other connected clients
            # and optionally display
            self.broadcast_message(message, sender)
            if self.mode == 'visual':
                chatref.display_message_main(message)
    #

    def start_client(self, chatref):
        # start listening for any message broadcast by the server
        self.answer_listener = threading.Thread(target=self.wait_for_response, args=(chatref, ))
        self.answer_listener.start()

        self.Frodo = FrodoAPI()
        print("frodoAPI: ", self.Frodo)

        # Start secure connection
        # self.server_pk = self.request_secure_conn_from_server()
        print("reading key")
        self.Frodo.set_public_key(list(open('server_pk.key', 'rb').read()))
        # print("pk: ", self.server_pk)
        # self.Frodo.set_public_key(self.server_pk)
        # self.ct, self.shared_secret = self.Frodo.crypto_kem_enc_frodo640()
        c, ss = self.Frodo.crypto_kem_enc_frodo640()
        open('server_c.key', 'wb').write(bytearray(c))
        print('client ss: ', ss)
        sleep(1)
        self.send_encrypted_secret_to_server([1,2,3])
        # print("ct: ", self.ct)
        # print("shared: ", self.shared_secret)
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

    # Send message to the server
    def send_message(self, message):
        message['port'] = self.client_port
        response = self.remote.send_message(message)
        self.log(f"[*] Sending message returned: {response.decode()}")
    #

    # Request public key from server
    def request_secure_conn_from_server(self):
        server_public_key = list(self.remote.get_key())
        return server_public_key
    #

    # After receiving public key calculate shared secret and ciphertext.
    # Next - send ciphertext back to the server (LWE-based key exchange)
    def send_encrypted_secret_to_server(self, ciphertext):
        self.remote.send_ciphertext(list(bytearray(ciphertext)))
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

        # print("REC: ", data)
        # print("end of data: ")

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
                self.log(f"[!] Incorrect argument type - expected: {arg_type} got: {type(remote_arg)}")
                client.close()
                return

        # Returned by RPC server function
        received = func['f'](*remote_args)

        # Client requested some action from server instead of sending message
        if 'action' in received:
            # Client requested server's public key
            if received['action'] == 'request_secure_connection':
                # Return server's public key
                #key = bytearray(list(self.server_pk))
                key = bytearray([1,2,3])
                client.sendall(struct.pack("<I", len(key)))
                client.sendall(key)
                self.log(f"[*] Sending server's public key back to the client: {client}")
                return
        # After public key is sent, client will send back ciphertext
        elif 'ciphertext' in received:
            self.secure_connection = True
            # print("ciphertext: ", received['ciphertext'])

            self.Frodo.set_ciphertext(list(open('server_c.key', 'rb').read()))
            ss1 = self.Frodo.crypto_kem_dec_frodo640()
            print('server ss: ', ss1)
            exit(-1)

            # self.Frodo.set_ciphertext(list(received['ciphertext']))
            # shared = self.Frodo.crypto_kem_dec_frodo640()
            # print("shared: ", shared)
            client.sendall(struct.pack("<I", len(self.success)))
            client.sendall(self.success)
            return


        else:
            # Default action is sending message
            # If reach this point, inform user that function succeeded
            client.sendall(struct.pack("<I", len(self.success)))
            client.sendall(self.success)

        return received
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
            'send_message': { 'argv': [dict], 'f': self.rpc_send_message},
            'get_key': { 'argv': [], 'f': self.rpc_get_public_keyKEM},
            'send_ciphertext': { 'argv': [list], 'f': self.rpc_send_ciphetextKEM}}
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
                received_data = self.socket.recv(data_len)

                # If server responded return received data
                if received_data:
                    return received_data

                self.disconnect()

            return worker
        #

        def rpc_send_message(self, message):
            return message
        #

        def rpc_get_public_keyKEM(self):
            return {'action': 'request_secure_connection'}
        #

        def rpc_send_ciphetextKEM(self, ciphertext):
            return {'ciphertext': ciphertext}
        #
    #
#