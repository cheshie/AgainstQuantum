#!/bin/python3

from FrodoKEM.frodo640.api_frodo640 import FrodoAPI640
from FrodoKEM.tests.test_kem import kem_test, kem_bench
from Application.ConnectionManager import ConnectionManager
import argparse
import sys

# class OutputManager:
#     @staticmethod
#     def output(list_args, where=print):
#         where(list_args)

#-----------------------------------------
# ME ?> dasdasdasd
# YOU ?> adasdasdasdasdasdassfadss
#
#
#-----------------------------------------
# ME ?> dasdasdas
#-----------------------------------------


def parse_arguments(args_parser = argparse.ArgumentParser(prog='appname', description='program description')):
    args_parser.add_argument('-p', help='connection port')
    args_parser.add_argument('-a', help='connection address')
    args_parser.add_argument('-i', help='start interactive mode. Commands available in the interactive mode:')
    args_parser.add_argument('-f', help='send file')
    args_parser.add_argument('-l', help='start server', action='store_true', default=False)
    args_parser.add_argument('-c', help='connect to a server', action='store_true', default=False)
    args_parser.add_argument('--secure', help='starts secure connection', action='store_true', default=False)
    args_parser.add_argument('--test', help='time benchmark of [operations]', action='store_true', default=False)
    args_parser.add_argument('--operations', help='possible operations are:'
                                                  'keyGeneration, encapsulation, decapsulation',
                             default='keyGeneration')
    args_parser.add_argument('--fails', help='test only if encapsulation matches decapsulation,'
                                             'do not measure time', action='store_true', default=False)
    args_parser.add_argument('--repeat', help='How many times to repeat time measurement', default=2)
    args_parser.add_argument('--number', help='How many times execute specified operations', default=2)

    if len(sys.argv) == 1:
        args_parser.print_help()

    return args_parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.c is True:
        ConnectionManager().start_client()
    if args.l is True:
        ConnectionManager().start_server()

    if args.test is True:
        if args.fails is True:
            kem_test(FrodoAPI640.CRYPTO_ALGNAME, iterations=int(args.number))
        else:
            kem_bench(repetitions=(int(args.number)))
#