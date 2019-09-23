import config
from numpy import zeros, uint16, frombuffer, uint32

"""
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: matrix arithmetic functions used by the KEM
"""


def frodo_mul_add_as_plus_e(out, s, e, seed_A, **params):
    # Generate - and -multiply: generate matrix A(N x N) row - wise, multiply by s on the right.
    # Inputs: s, e(N x N_BAR)
    # Output: out = A * s + e(N x N_BAR)


    # ALIGN_HEADER and FOOTER from config are used here
    a_row = zeros(4*params['PARAMS_N'],dtype=uint16)

    out = e

    # If USE_AES128_FOR_A defined
    a_row_temp = zeros(4*params['PARAMS_N'], dtype=uint16)

    # EVP_CIPHER_CTX ==> WHAT IS IT??
    # Haven't checked if above works. Need more tests



    # for i in range(0,params['PARAMS_N']*params['PARAMS_NBAR'],2):
        # out[i] =


    pass
#


def frodo_mul_add_sa_plus_e(out, s, e, seed_A):
    pass
#


def frodo_mul_bs(out, b, s):
    pass
#


def frodo_mul_add_sb_plus_e(out, b, s, e):
    pass
#


def frodo_add(out, a, b):
    pass
#


def frodo_sub(out, a, b):
    pass
#


def frodo_key_encode():
    pass
#


def frodo_key_decode():
    pass
#