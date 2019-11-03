from numpy import uint16, array

from src.kem import crypto_kem_dec, crypto_kem_enc, crypto_kem_keypair
from src.sha3.shafips202 import shake128

"""
********************************************************************************************
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: parameters and API for FrodoKEM-640
functions for FrodoKEM-640
*           Instantiates "frodo_macrify.c" with the necessary matrix arithmetic functions
*********************************************************************************************/
"""

CRYPTO_ALGNAME = "FrodoKEM-640"

# Parameters for FrodoKEM-640
FrodoKEM640Params = {
    'CRYPTO_SECRETKEYBYTES'  : 19888,     # sizeof(s) + 'CRYPTO_PUBLICKEYBYTES' + 2*'PARAMS_N'*'PARAMS_NBAR' + 'BYTES_PKHASH'
    'CRYPTO_PUBLICKEYBYTES'   : 9616,     # sizeof('seed_A') + ('PARAMS_LOGQ'*'PARAMS_N'*'PARAMS_NBAR')/8
    'CRYPTO_BYTES'              : 16,
    'CRYPTO_CIPHERTEXTBYTES'  : 9720,     # (PARAMS_LOGQ*PARAMS_N*PARAMS_NBAR)/8 + (PARAMS_LOGQ*PARAMS_NBAR*PARAMS_NBAR)/8
    'PARAMS_N' :  640,
    'PARAMS_NBAR' :  8,
    'PARAMS_LOGQ' :  15,
    'PARAMS_Q' :  1 << 15, # PARAMS_LOGQ
    'PARAMS_EXTRACTED_BITS' :  2,
    'PARAMS_STRIPE_STEP' :  8,
    'PARAMS_PARALLEL' :  4,
    'BYTES_SEED_A' :  16,
    'BYTES_MU' :  (2*8*8)//8, #(PARAMS_EXTRACTED_BITS*PARAMS_NBAR*PARAMS_NBAR)
    'BYTES_PKHASH' :  16
}

# Selecting SHAKE XOF function for the KEM and noise sampling
shake = shake128

# CDF table
CDF_TABLE_LEN = 13
CDF_TABLE = array([4643, 13363, 20579, 25843, 29227, 31145, 32103, 32525, 32689, 32745, 32762, 32766, 32767],dtype=uint16)
FrodoKEM640Params['CDF_TABLE'] = CDF_TABLE
FrodoKEM640Params['CDF_TABLE_LEN'] = CDF_TABLE_LEN


# FrodoKEM-640 functions
def crypto_kem_keypair_frodo640(pk, sk):
    crypto_kem_keypair(pk, sk, shake, **FrodoKEM640Params)


def crypto_kem_enc_frodo640(ct, ss, pk):
    crypto_kem_enc(ct, ss, pk, shake, **FrodoKEM640Params)


def crypto_kem_dec_frodo640(ss, ct, sk):
    crypto_kem_dec(ss, ct, sk, shake, **FrodoKEM640Params)
