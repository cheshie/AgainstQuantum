from numpy import uint16, array, array, zeros, uint8, uint16, frombuffer, copyto

from src.kem import CryptoKem
from src.sha3.shafips202 import shake128

empty = zeros

"""
********************************************************************************************
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: parameters and API for FrodoKEM-640
functions for FrodoKEM-640
*           Instantiates "frodo_macrify.c" with the necessary matrix arithmetic functions
*********************************************************************************************/
"""

class FrodoAPI640():
    def __init__(self):
        self.CRYPTO_ALGNAME = "FrodoKEM-640"

        # Parameters for FrodoKEM-640
        self.CRYPTO_SECRETKEYBYTES =  19888,     # sizeof(s) + 'CRYPTO_PUBLICKEYBYTES' + 2*'PARAMS_N'*'PARAMS_NBAR' + 'BYTES_PKHASH'
        self.CRYPTO_PUBLICKEYBYTES =  9616,     # sizeof('seed_A') + ('PARAMS_LOGQ'*'PARAMS_N'*'PARAMS_NBAR')/8
        self.CRYPTO_BYTES =  16,
        self.CRYPTO_CIPHERTEXTBYTES =  9720,     # (PARAMS_LOGQ*PARAMS_N*PARAMS_NBAR)/8 + (PARAMS_LOGQ*PARAMS_NBAR*PARAMS_NBAR)/8
        self.PARAMS_N =   640,
        self.PARAMS_NBAR =   8,
        self.PARAMS_LOGQ =   15,
        self.PARAMS_Q =   1 << 15, # PARAMS_LOGQ
        self.PARAMS_EXTRACTED_BITS =   2,
        self.PARAMS_STRIPE_STEP =   8,
        self.PARAMS_PARALLEL =   4,
        self.BYTES_SEED_A =   16,
        self.BYTES_MU =   (2*8*8)//8, #(PARAMS_EXTRACTED_BITS*PARAMS_NBAR*PARAMS_NBAR)
        self.BYTES_PKHASH =   16
        # CDF table
        self.CDF_TABLE_LEN = 13
        self.CDF_TABLE = array([4643, 13363, 20579, 25843, 29227, 31145, 32103, 32525, 32689, 32745, 32762, 32766, 32767], dtype=uint16)

        # Selecting SHAKE XOF function for the KEM and noise sampling
        self.shake = shake128

        # Data - vectors
        self.pk = zeros(self.CRYPTO_PUBLICKEYBYTES, dtype=uint8)
        self.sk = zeros(self.CRYPTO_SECRETKEYBYTES, dtype=uint8)
        self.ss_encap = empty(self.CRYPTO_BYTES, dtype=uint8)
        self.ss_decap = empty(self.CRYPTO_BYTES, dtype=uint8)
        self.ct = empty(self.CRYPTO_CIPHERTEXTBYTES, dtype=uint8)

    # FrodoKEM-640 functions
    def crypto_kem_keypair_frodo640(self):
        CryptoKem.keypair(self, self.pk, self.sk)


    def crypto_kem_enc_frodo640(self):
        CryptoKem.enc(self, self.ct, self.ss_encap, self.pk)


    def crypto_kem_dec_frodo640(self):
        CryptoKem.dec(self, self.ss_decap, self.ct, self.sk)
