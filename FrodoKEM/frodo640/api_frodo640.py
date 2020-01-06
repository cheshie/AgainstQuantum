from numpy import array, zeros, uint8, uint16
from FrodoKEM.src.kem import CryptoKem
from FrodoKEM.src.sha3.shafips202 import SHA202

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
        CRYPTO_ALGNAME = "FrodoKEM-640"
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

        def __init__(self):
            self.pk = zeros(self.CRYPTO_PUBLICKEYBYTES, dtype=uint8)
            self.sk = zeros(self.CRYPTO_SECRETKEYBYTES, dtype=uint8)
            self.ss_encap = zeros(self.CRYPTO_BYTES, dtype=uint8)
            self.ss_decap = zeros(self.CRYPTO_BYTES, dtype=uint8)
            self.ct = zeros(self.CRYPTO_CIPHERTEXTBYTES, dtype=uint8)
        #

        # Functions that allow external classes to set own FrodoKEM properties
        # For shared secret generation
        def set_public_key(self, public_key: 'external public key [list]'):
            if len(public_key) == len(self.pk):
                self.pk = array(public_key, dtype=uint8)
            else:
                raise Exception('Provided key size differs from that in parameters.')
        #
        def set_secret_key(self, secret_key: 'external secret key [list]'):
            if len(secret_key) == len(self.sk):
                self.sk = array(secret_key, dtype=uint8)
            else:
                raise Exception('Provided key size differs from that in parameters.')
        #

        def set_ciphertext(self, ciphertext: 'external ciphertext [list]'):
            if len(ciphertext) == len(self.ct):
                self.ct = array(ciphertext, dtype=uint8)
            else:
                raise Exception('Provided key size differs from that in parameters.')
        #
    #

    # FrodoKEM class system parameters
    kem = Params()

    # FrodoKEM-640 functions
    @classmethod
    def crypto_kem_keypair_frodo640(cls):
        cls.kem = cls.Params()
        return CryptoKem.keypair(cls.kem, cls.kem.pk, cls.kem.sk)
    #

    @classmethod
    def crypto_kem_enc_frodo640(cls):
        return CryptoKem.enc(cls.kem, cls.kem.ct, cls.kem.ss_encap, cls.kem.pk.copy())
    #
    @classmethod
    def crypto_kem_dec_frodo640(cls):
        return CryptoKem.dec(cls.kem, cls.kem.ss_decap, cls.kem.ct.copy(), cls.kem.sk.copy())
    #
#