from kem import crypto_kem_dec, crypto_kem_enc, crypto_kem_keypair
from ctypes import c_uint16
from shafips202 import shake128

"""
********************************************************************************************
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: parameters and API for FrodoKEM-640
functions for FrodoKEM-640
*           Instantiates "frodo_macrify.c" with the necessary matrix arithmetic functions
*********************************************************************************************/
"""

CRYPTO_SECRETKEYBYTES  = 19888     # sizeof(s) + CRYPTO_PUBLICKEYBYTES + 2*PARAMS_N*PARAMS_NBAR + BYTES_PKHASH
CRYPTO_PUBLICKEYBYTES   = 9616     # sizeof(seed_A) + (PARAMS_LOGQ*PARAMS_N*PARAMS_NBAR)/8
CRYPTO_BYTES              = 16
CRYPTO_CIPHERTEXTBYTES  = 9720     # (PARAMS_LOGQ*PARAMS_N*PARAMS_NBAR)/8 + (PARAMS_LOGQ*PARAMS_NBAR*PARAMS_NBAR)/8

CRYPTO_ALGNAME = "FrodoKEM-640"

# Parameters for FrodoKEM-640
FrodoKEM640Params = {
    'PARAMS_N' :  640,
    'PARAMS_NBAR' :  8,
    'PARAMS_LOGQ' :  15,
    'PARAMS_Q' :  1 << 15, # PARAMS_LOGQ
    'PARAMS_EXTRACTED_BITS' :  2,
    'PARAMS_STRIPE_STEP' :  8,
    'PARAMS_PARALLEL' :  4,
    'BYTES_SEED_A' :  16,
    'BYTES_MU' :  (2*8*8)/8, #(PARAMS_EXTRACTED_BITS*PARAMS_NBAR*PARAMS_NBAR)
    'BYTES_PKHASH' :  CRYPTO_BYTES
}

# Selecting SHAKE XOF function for the KEM and noise sampling
shake = shake128

# CDF table
CDF_TABLE_LEN = 13;
CDF_TABLE = c_uint16 * CDF_TABLE_LEN
CDF_TABLE = CDF_TABLE(4643, 13363, 20579, 25843, 29227, 31145, 32103, 32525, 32689, 32745, 32762, 32766, 32767)
FrodoKEM640Params['CDF_TABLE'] = CDF_TABLE

# FrodoKEM-640 functions
def crypto_kem_keypair_Frodo640(pk, sk):
    print("Accessed funtion - executing: ")
    crypto_kem_keypair(pk, sk, **FrodoKEM640Params)


def crypto_kem_enc_Frodo640(ct, ss, pk):
    print("Accessed funtion - executing: ")
    crypto_kem_enc(ct, ss, pk, **FrodoKEM640Params)


def crypto_kem_dec_Frodo640(ss, ct, sk):
    print("Accessed funtion - executing: ")
    crypto_kem_enc(ss, ct, sk, **FrodoKEM640Params)
