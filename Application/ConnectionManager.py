import socket
import threading
import struct
import json
import random
from time import sleep
from datetime import datetime
from FrodoKEM.frodo640.api_frodo640 import FrodoAPI640 as FrodoAPI
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from binascii import hexlify, unhexlify


class ConnectionManager:
    # Text mode or graphical mode. Is set in class instance
    mode = None

    def __init__(self, mode='text', socket_type = socket.SOCK_STREAM, setup=None):
        # For both server and client
        self.socket = socket.socket(socket.AF_INET, socket_type)

        # For server - it will listen on this pair
        # For client - it will connect using this pair
        self.ip   = "0.0.0.0" if setup['a'] is None else setup['a']
        self.port = 9999 if setup['p'] is None else setup['p']

        # Client will listen on this port and addr for any messages sent to
        # The server by other users
        self.client_ip = "0.0.0.0"
        self.client_port = 9777 if setup['clport'] is None else setup['clport']

        # Maintain a list of all connections to the server (list of sockets, list of IPs, list of ports)
        self.server_conns = (list(), list(), list())
        ConnectionManager.mode = mode

        self.server_limit = 5 if setup['svconn'] is None else int(setup['svconn'])

        # Class that brings RPC capability, default success response for its functions
        self.remote = self.RemoteAPI(self.ip, self.port)
        self.success = json.dumps({'code': 200}).encode()
        self.error_insecure = json.dumps({'code': 401}).encode()

        # True if user requested secure connection, otherwise all data will be sent
        # in plaintext
        self.encryption =  False if setup['secure'] is None else setup['secure']
        self.KeyExchange = self.KeyExchanger()
    #

    def __del__(self):
        if hasattr(self, 'answer_listener'):
            self.answer_listener.join()
    #

    def start_server(self, chatref):
        # Start the server on specific IP and port listening on
        self.socket.bind((self.ip, self.port))

        # Server start listening with a max backlog of connections set to 5
        self.socket.listen(self.server_limit)

        self.log("[*] Listening on %s:%d" % (self.ip, self.port))

        if self.encryption:
            self.KeyExchange.generate_keypair()

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

            # If user sent message broadcast it to other connected clients
            # and optionally display
            self.broadcast_message(message, sender)
            if self.mode == 'visual':
                chatref.display_message_main(message)
    #

    def start_client(self, chatref):
        try:
            # Firstly try to connect to the server - securely or just check if its alive
            if self.encryption:
                try:
                    self.KeyExchange.connect_to_server(self.remote)
                except Exception as ex:
                    self.log(f"[!] Key exchange failed. Reason: {ex}")
                    exit(-1)
            else:
                serv_status = self.check_server_is_online()
                if serv_status['code'] == 401:
                    self.log('[!] This server is secure. Connect with --secure option. Exiting')
                    exit(-1)
                self.log("[*] Client started without --secure option, connection will be insecure")

            # start listening for any message broadcast by the server
            self.answer_listener = threading.Thread(target=self.wait_for_response, args=(chatref, ))
            self.answer_listener.start()

            if self.encryption and self.KeyExchange.secure_connection:
                self.Enc = self.Encryption(bytes(self.KeyExchange.shared_secret))
                self.log("[*] Connection with the server is now secure.")
        except KeyboardInterrupt:
            self.answer_listener.alive = False
            self.answer_listener.join()
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
            con = None
            try:
                con, add = self.client_socket.accept()
                # Receive information about size of message sent by the server
                # and then receive and display the message
                size = struct.unpack('<I', con.recv(4))[0]
                chatref.display_message_main(json.loads(con.recv(size).decode()), reset=True)
                con.close()
            except KeyboardInterrupt:
                if con is not None:
                    con.close()
                return
    #

    # Send message to the server
    def send_message(self, message):
        message['port'] = self.client_port

        if self.encryption and self.KeyExchange.secure_connection:
            message['nick'] = self.Enc.encrypt_message(message['nick'])
            message['msg']  = self.Enc.encrypt_message(message['msg'])
            message['port'] = self.Enc.encrypt_message(str(message['port']))

        response = self.remote.send_message(message)
        self.log(f"[*] Sending message returned: {response.decode()}", file=True)
    #

    # method for client to check if server is working
    def check_server_is_online(self):
        return json.loads(self.remote.check_server({'action' : 'check_server_alive'}))
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
        try:
            # Interpret sent structure into function
            ConnectionManager.log("[*] JSON Data from client received. Trying to decode it...")
            remote_name = json.loads(data)['func']
            remote_args = tuple(json.loads(data)['argv'])
        except Exception as ex:
            ConnectionManager.log(f"[!] Error while trying to decode incorrect user request. Skipping this request.\n => Reason: {ex}")
            return None
        else:
            ConnectionManager.log( f"[*] Data decoded. Processing client's request.")

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
            self.KeyExchange.calculate_shared_secret_server_FrodoKEM(received_data=received, client=client)

            # Client 'pings' server
            if received['action'] == 'check_server_alive':
                # If server is secure and an insecure client connects, send error
                # Otherwise confirm that server is alive
                if self.encryption is True:
                    self.log(f"[*] Insecure client tried to connect, denied: {client}")
                    client.sendall(struct.pack("<I", len(self.error_insecure)))
                    client.sendall(self.error_insecure)
                else:
                    client.sendall(struct.pack("<I", len(self.success)))
                    client.sendall(self.success)
                    self.log(f"[*] Sending server's status to the client: {client}")
                return None
            #

            # If user requested information from server
            if isinstance(received['action'], dict) == False:
                self.log(f"[*] Sending server's public key back to the client: {client}")

            if hasattr(self.KeyExchange, 'shared_secret'):
                self.Enc = self.Encryption(bytes(self.KeyExchange.shared_secret))
                self.log(f"[*] Connection secured with client: {client}")

            return None
        else:
            # Decrypt message from user
            if self.KeyExchange.secure_connection:
                if isinstance(received['port'], int):
                    self.log(f"[!] Insecure user connected to the chat")
                    client.sendall(struct.pack("<I", len(self.error_insecure)))
                    client.sendall(self.error_insecure)
                    return None
                else:
                    received['nick'] = self.Enc.decrypt_message(received['nick'])
                    received['msg'] = self.Enc.decrypt_message(received['msg'])
                    received['port'] = self.Enc.decrypt_message(str(received['port']))

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
            self.log(f"[*] New sender added: {addr[0]}:{port}")

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

    @classmethod
    def log(cls, msg, file=False):
        if cls.mode == 'text' and file == False:
            print(msg)
        elif cls.mode == 'visual' or file == True:
            logfile = open(datetime.now().strftime("%m-%d-%Y"+".log"), 'a+')
            logfile.write(datetime.now().strftime("%H:%M:%S") + " : " + msg + '\n')
    #

    class Encryption():
        def __init__(self, key):
            # Key provided here as a list of bytes, will be encoded below to a raw bytes
            self.key = key
        #

        # Take message in str format, decrypt it and return hex data ready to send
        # Default encoding is hex
        # Takes str, returns str
        def encrypt_message(self, message):
            try:
                ciphertext =  AES.new(self.key, AES.MODE_ECB).encrypt(pad(message.encode(), AES.block_size,  style='pkcs7'))
            except Exception as ex:
                ConnectionManager.log(f"[!] Error while encrypting message. Returning string \"not encrypted\". Reason: \n => {ex}")
                return "not encrypted"
            return hexlify(ciphertext).decode()
        #

        # Decrypt received data in str format
        # Default encoding is hex
        # Takes str, returns bytes
        def decrypt_message(self, message):
            try:
                raw = unpad(AES.new(self.key, AES.MODE_ECB).decrypt(unhexlify(message)) , AES.block_size,  style='pkcs7')
            except Exception as ex:
                ConnectionManager.log(f"[!] Error while decrypting message. Returning string \"not encrypted\". Reason: \n => {ex}")
                return "not decrypted"

            return raw.decode()
        #
    #

    # Class that provide key exchange mechanism to secure communication
    class KeyExchanger():
        def __init__(self):
            # Key Exchange algorithm - default is FrodoKEM-640
            self.ExchangeAlgorithm = FrodoAPI()

            # Define functions based on specific key exchange system used
            if self.ExchangeAlgorithm.kem.CRYPTO_ALGNAME == 'FrodoKEM-640':
                self.keypair_generation = self.ExchangeAlgorithm.crypto_kem_keypair_frodo640
                self.key_encryption = self.ExchangeAlgorithm.crypto_kem_enc_frodo640
                self.key_decryption = self.ExchangeAlgorithm.crypto_kem_dec_frodo640
            #

            # Online mode - sockets, Offline mode - files
            # It defines way in cl and serv communicate cipher parameters
            self.mode = 'online'
            self.server_pk = None
            self.server_sk = None
            # Will change to true if key exchange was successful
            self.secure_connection = False
        #

        # Server must generate own pair of keys (public, private)
        def generate_keypair(self):
            ConnectionManager.log("[*] Generating server's key pair...")
            try:
                self.server_pk, self.server_sk = self.keypair_generation()
            except Exception as ex:
                ConnectionManager.log(f"FrodoKEM KeyGeneration Error. Please restart the server. \nReason => {ex}")
            # Offline mode means connecting through files, not sockets (debugging mode)
            ConnectionManager.log("[*] Keys successfully generated")
            if self.mode == 'offline':
                open('server_pk.key', 'wb').write(bytearray(self.server_pk))
        #

        # Client requests public key from server
        def connect_to_server(self, remote):
            if self.mode == 'online':
                self.server_pk = remote.key_exchange({'action': 'request_secure_connection'})
            else:
                self.server_pk = list(open('server_pk.key', 'rb').read())

            self.get_shared_secret_client(remote)
        #

        # Getting shared secret specific for LWEKE scheme
        def get_shared_secret_client_FrodoKEM(self, remote):
            # Set public key received from the server
            if self.mode == 'online':
                self.ExchangeAlgorithm.kem.set_public_key(list(self.server_pk))
            else:
                self.ExchangeAlgorithm.kem.set_public_key(list(open('server_pk.key', 'rb').read()))

            # Generate shared secret
            # TODO: Key encryption issues
            # In short - key encryption is not deterministic (by design ofc). This means, each time
            # each new client will generate completely different shared secret, whereas
            # server's key decryption is fully deterministic.
            self.ct, self.shared_secret = self.key_encryption()

            # After receiving public key calculate shared secret and ciphertext.
            # Next - send ciphertext back to the server (LWE-based key exchange)
            try:
                if self.mode == 'online':
                    remote.key_exchange({'action': {'ciphertext': list(bytearray(list(self.ct)))}})
                    open('server_c.key', 'wb').write(bytearray(list(self.ct)))
                else:
                    open('server_c.key', 'wb').write(bytearray(list(self.ct)))
            except OSError as oerr:
                ConnectionManager.log(f"[!] Failed writing to the log file. Check permissions. Reason: {oerr}")

            self.secure_connection = True
        #

        def calculate_shared_secret_server_FrodoKEM(self, received_data, client):
            # Client requested server's public key
            if isinstance(received_data['action'], dict) == False:
                if received_data['action'] == 'request_secure_connection':
                    # Return server's public key
                    key = bytearray(list(self.server_pk))
                    client.sendall(struct.pack("<I", len(key)))
                    client.sendall(key)
            # After public key is sent, client will send back ciphertext
            elif 'ciphertext' in received_data['action'].keys():
                if hasattr(self, 'shared_secret') == False:
                    if self.mode == 'online':
                        self.ExchangeAlgorithm.kem.set_ciphertext(received_data['action']['ciphertext'])
                    else:
                        self.ExchangeAlgorithm.kem.set_ciphertext(list(open('server_c.key', 'rb').read()))

                    try:
                        # Calculate shared secret
                        ConnectionManager.log("[*] FrodoKEM: Decrypting key received from the client to calculate shared secret...")
                        self.shared_secret = self.key_decryption()
                        self.secure_connection = True
                    except Exception as ex:
                            ConnectionManager.log(f"[!] FrodoKEM KeyDecryption() Error. Please restart the server. \nReason => {ex}")
                    else:
                        ConnectionManager.log("[*] FrodoKEM: Shared secret calculated successfully")

                # Send back information to client about successful key exchange
                client.sendall(struct.pack("<I", len(json.dumps({'code': 200}).encode())))
                client.sendall(json.dumps({'code': 200}).encode())
        #

        def get_shared_secret_client(self, remote):
            self.get_shared_secret_client_FrodoKEM(remote)
        #
    #

    class RemoteAPI:
        def __init__(self, ip, port):
            self.ip = ip
            self.port = port
            self.shared = {
            'send_message': { 'argv': [dict], 'f': self.rpc_send_message},
            'key_exchange': { 'argv': [dict], 'f': self.rpc_key_exchange},
            'check_server': { 'argv': [dict], 'f': self.rpc_check_server}}
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
                try:
                    self.connect()
                except Exception as ex:
                    ConnectionManager.log("[!] Connection to the server failed. See log file for details. Exiting")
                    ConnectionManager.log(f"Reason: {ex}", file=True)
                    exit(-1)

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

        def rpc_key_exchange(self, request):
            return request
        #
        def rpc_check_server(self, request):
            return request
    #
#