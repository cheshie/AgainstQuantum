from FrodoKEM.frodo640.api_frodo640 import FrodoAPI640
from ConnectionManager import ConnectionManager

# class OutputManager:
#     @staticmethod
#     def output(list_args, where=print):
#         where(list_args)

if __name__ == "__main__":
    print("Hello in the console application. ")
    connectionManager = ConnectionManager()
    connectionManager.start_client()
    # exit()


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

