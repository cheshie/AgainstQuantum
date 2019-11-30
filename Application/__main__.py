#!/bin/python3

from FrodoKEM.frodo640.api_frodo640 import FrodoAPI640
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


def parse_arguments(args_parser = argparse.ArgumentParser()):
    args_parser.add_argument('-p', help='connection port')
    args_parser.add_argument('-a', help='connection address')
    args_parser.add_argument('-i', help='start interactive mode. Commands available in the interactive mode:')
    args_parser.add_argument('-f', help='send file')
    args_parser.add_argument('-l', help='start server', action='store_true', default=False)
    args_parser.add_argument('-c', help='connect to a server', action='store_true', default=False)
    args_parser.add_argument('--secure', help='starts secure connection')
    args = args_parser.parse_args()

    #args_parser.set_defaults()

    if len(sys.argv) == 1:
        args_parser.print_help()

    return args


if __name__ == "__main__":
    args = parse_arguments()
    connectionManager = ConnectionManager()

    if args.c is True:
        connectionManager.start_client()
    if args.l is True:
        connectionManager.start_server()

    exit()


    # print("Hello in the console application. ")



    # FrodoAPI640 = FrodoAPI640()
    # crypto_kem_keypair = FrodoAPI640.crypto_kem_keypair_frodo640
    # crypto_kem_enc = FrodoAPI640.crypto_kem_enc_frodo640
    # crypto_kem_dec = FrodoAPI640.crypto_kem_dec_frodo640
    #
    # for x in range(2):
    #     crypto_kem_keypair()
    #     ss_encap = crypto_kem_enc()
    #     ss_decap = crypto_kem_dec()
    #
    #     if ss_encap.all() == ss_decap.all() is not True:
    #         print("ERROR!")
    #     else:
    #         print("Keys equal.")
    #