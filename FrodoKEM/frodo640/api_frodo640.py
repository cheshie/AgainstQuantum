from numpy import array, zeros, uint8, uint16
from src.kem import CryptoKem
from src.sha3.shafips202 import SHA202

empty = zeros

"""
********************************************************************************************
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: parameters and API for FrodoKEM-640 functions for FrodoKEM-640
*           Instantiates "frodo_macrify.c" with the necessary matrix arithmetic functions
*********************************************************************************************/
"""


class FrodoAPI640(CryptoKem):
    class Params():
        # Parameters for FrodoKEM-640
        CRYPTO_SECRETKEYBYTES = 19888  # sizeof(s) + 'CRYPTO_PUBLICKEYBYTES' + 2*'PARAMS_N'*'PARAMS_NBAR' + 'BYTES_PKHASH'
        CRYPTO_PUBLICKEYBYTES = 9616  # sizeof('seed_A') + ('PARAMS_LOGQ'*'PARAMS_N'*'PARAMS_NBAR')/8
        CRYPTO_BYTES = 16
        CRYPTO_CIPHERTEXTBYTES = 9720  # (PARAMS_LOGQ*PARAMS_N*PARAMS_NBAR)/8 + (PARAMS_LOGQ*PARAMS_NBAR*PARAMS_NBAR)/8
        PARAMS_N = 640
        PARAMS_NBAR = 8
        PARAMS_LOGQ = 15
        PARAMS_Q = 1 << 15  # PARAMS_LOGQ
        PARAMS_EXTRACTED_BITS = 2
        PARAMS_STRIPE_STEP = 8
        PARAMS_PARALLEL = 4
        BYTES_SEED_A = 16
        BYTES_MU = (2 * 8 * 8) // 8  # (PARAMS_EXTRACTED_BITS*PARAMS_NBAR*PARAMS_NBAR)
        BYTES_PKHASH = 16

        # CDF table
        CDF_TABLE_LEN = 13
        CDF_TABLE = array(
            [4643, 13363, 20579, 25843, 29227, 31145, 32103, 32525, 32689, 32745, 32762, 32766, 32767], dtype=uint16)

        # Selecting SHAKE XOF function for the KEM and noise sampling
        shake = SHA202.shake128
    #

    Params = Params()
    CRYPTO_ALGNAME = "FrodoKEM-640"

    def initialize(self):
        # Data - vectors initialization
        self.pk = zeros(self.Params.CRYPTO_PUBLICKEYBYTES, dtype=uint8)
        self.sk = zeros(self.Params.CRYPTO_SECRETKEYBYTES, dtype=uint8)
        self.ss_encap = empty(self.Params.CRYPTO_BYTES, dtype=uint8)
        self.ss_decap = empty(self.Params.CRYPTO_BYTES, dtype=uint8)
        self.ct = empty(self.Params.CRYPTO_CIPHERTEXTBYTES, dtype=uint8)
    #

    def __init__(self):
        self.initialize()
    #

    # FrodoKEM-640 functions
    @classmethod
    def crypto_kem_keypair_frodo640(cls):
        cls.initialize(cls)
        return CryptoKem.keypair(cls.Params, cls.pk, cls.sk)
    #
    @classmethod
    def crypto_kem_enc_frodo640(cls):
        return CryptoKem.enc(cls.Params, cls.ct, cls.ss_encap, cls.pk)
    #
    @classmethod
    def crypto_kem_dec_frodo640(cls):
        return CryptoKem.dec(cls.Params, cls.ss_decap, cls.ct, cls.sk)
    #
#