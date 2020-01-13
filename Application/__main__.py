#!/bin/python3

from FrodoKEM.frodo640.api_frodo640 import FrodoAPI640
from FrodoKEM.tests.test_kem import kem_test, kem_bench
from Application.ChatManager import ChatManager
import argparse
import sys

# Parse command line arguments
def parse_arguments(args_parser = argparse.ArgumentParser(prog='Application', description='Chat and key exchange testing')):
    # Arguments connected with ConnectionManager class -> managing connections
    clientserv = args_parser.add_argument_group('client-server basic options')
    # Arguments connected with ChatManager class -> managing chat
    chat = args_parser.add_argument_group('chat options')
    # Arguments connected with benchmarking FrodoKEM or any other connected key exchange protocol
    tests = args_parser.add_argument_group('testing key exchange')

    clientserv.add_argument('-p', help='connection port')
    clientserv.add_argument('-a', help='connection address')
    clientserv.add_argument('-l', help='start server', action='store_true', default=False)
    clientserv.add_argument('--svconn', help='number of clients that can be connected to the server at the time')
    clientserv.add_argument('-c', help='connect to a server', action='store_true', default=False)
    clientserv.add_argument('-f', help='send file to the server - provide path to the file')
    clientserv.add_argument('--clport', help="change port on which client will listen for server's response (default 9777)")
    clientserv.add_argument('--secure', help='starts secure connection', action='store_true', default=False)
    chat.add_argument('--nick', help='change default-random nick')
    chat.add_argument('--mode', help='display mode', default='text', choices=['visual','text']) # metavar=('bar', 'baz'),
    tests.add_argument('--test', help='time benchmark of [operations]. Default is testing of all operations', action='store_true', default=False)
    tests.add_argument('--ops', help='possible operations are: keyGeneration, encapsulation, decapsulation',
                             default='keyGeneration')
    tests.add_argument('--fails', help='test only if encapsulation matches decapsulation,'
                                             'time benchmark is not the goal', action='store_true', default=False)
    tests.add_argument('--repeat', help='How many times to repeat time measurement', default=2)
    tests.add_argument('--number', help='How many times execute specified operations', default=2)
    tests.add_argument('--system', help='Choose FrodoKEM version\n (Frodo640, Frodo976, Frodo1344)',
                             default='Frodo640')

    if len(sys.argv) == 1:
        args_parser.print_help()

    # Return parsed arguments and a list containing dictionaries for separate groups
    return args_parser.parse_args(), dict([(group.title, {a.dest:getattr(args_parser.parse_args(), a.dest,None) for a in group._group_actions})
                   for group in args_parser._action_groups])
#


if __name__ == "__main__":
    args, arg_groups = parse_arguments()

    # Start client or server
    if args.c is True:
        ChatManager(chat=arg_groups['chat options'], connection=arg_groups['client-server basic options']).start_client()
    if args.l is True:
        ChatManager(chat=arg_groups['chat options'], connection=arg_groups['client-server basic options']).start_server()

    # Start benchmark
    if args.test is True:
        if args.fails is True:
            kem_test(FrodoAPI640.kem.CRYPTO_ALGNAME, iterations=int(args.repeat), system=args.system)
        else:
            if int(args.repeat) < 2:
                print("Error. Time measurement must be repeated at least 2 times (--repeat). Exiting")
                exit(-1)
            else:
                kem_bench(repetitions=(int(args.repeat)), kem_test_iterations=int(args.number), system=args.system)
#