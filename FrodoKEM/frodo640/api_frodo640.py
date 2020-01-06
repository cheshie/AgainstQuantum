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

        # MAYBE PARAMS HERE???
    #

    # FrodoKEM system parameters
    Params = Params()
    CRYPTO_ALGNAME = "FrodoKEM-640"
    pk = zeros(Params.CRYPTO_PUBLICKEYBYTES, dtype=uint8)
    sk = zeros(Params.CRYPTO_SECRETKEYBYTES, dtype=uint8)
    ss_encap = zeros(Params.CRYPTO_BYTES, dtype=uint8)
    ss_decap = zeros(Params.CRYPTO_BYTES, dtype=uint8)
    ct = zeros(Params.CRYPTO_CIPHERTEXTBYTES, dtype=uint8)

    # FrodoKEM-640 functions
    @classmethod
    def crypto_kem_keypair_frodo640(cls):
        # Re - initialization of Frodo640 class params for each key generation
        cls.pk = zeros(cls.Params.CRYPTO_PUBLICKEYBYTES, dtype=uint8)
        cls.sk = zeros(cls.Params.CRYPTO_SECRETKEYBYTES, dtype=uint8)
        cls.ss_encap = zeros(cls.Params.CRYPTO_BYTES, dtype=uint8)
        cls.ss_decap = zeros(cls.Params.CRYPTO_BYTES, dtype=uint8)
        cls.ct = zeros(cls.Params.CRYPTO_CIPHERTEXTBYTES, dtype=uint8)

        return CryptoKem.keypair(cls.Params, cls.pk, cls.sk)
    #
    @classmethod
    def crypto_kem_enc_frodo640(cls):
        print("before enc - pk: ", list(cls.pk)[-5:])
        print("before enc - sk: ", list(cls.sk)[-5:])
        print("before enc - encap: ", list(cls.ss_encap))
        print("before enc - decap: ", list(cls.ss_decap))
        print("before enc - ct: ", list(cls.ct)[-5:])
        # MAYBE SEND HERE COPIES OF PARAMS THAT DO NOT NEED TO CHANGE???
        return CryptoKem.enc(cls.Params, cls.ct, cls.ss_encap, cls.pk)
    #
    @classmethod
    def crypto_kem_dec_frodo640(cls):
        print("after enc - pk: ", list(cls.pk)[-5:])
        print("after enc - sk: ", list(cls.sk)[-5:])
        print("after enc - encap: ", list(cls.ss_encap)[-5:])
        print("after enc - decap: ", list(cls.ss_decap)[-5:])
        print("after enc - ct: ", list(cls.ct)[-5:])
        return CryptoKem.dec(cls.Params, cls.ss_decap, cls.ct, cls.sk)
    #

    # Functions that allow external classes to set own FrodoKEM properties
    # For shared secret generation
    def set_public_key(self, public_key: 'external public key [list]'):
        self.pk = array(public_key, dtype=uint8)
    #
    def set_secret_key(self, secret_key: 'external secret key [list]'):
        self.sk = array(secret_key, dtype=uint8)
    #

    def set_ciphertext(self, ciphertext: 'external ciphertext [list]'):
        self.ct = array(ciphertext, dtype=uint8)
    #
#