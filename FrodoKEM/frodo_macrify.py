import config
from numpy import zeros, uint16, frombuffer, uint32, uint8, array, sum, tile, split, copyto
from Crypto.Cipher import AES
from config import UINT16_TO_LE, LE_TO_UINT16
import trace

trace.debug_mode = False
trcl = trace.tracelst
trc = trace.trace

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

    copyto(out, e)

    # If USE_AES128_FOR_A defined
    a_row_temp = array(
        [UINT16_TO_LE(j - 1) if j % params['PARAMS_STRIPE_STEP'] - 1 == 0 else 0
         for j in range(params['PARAMS_N'])] * 4,
        dtype=uint16
    )

    # Create new EVP cipher object and pass key from pk
    cipher = AES.new(seed_A[:16], AES.MODE_ECB)

    # Temporary values to make below lines shorter
    max_tmp = 4 * params['PARAMS_N']
    par_n = params['PARAMS_N']
    par_nbar = params['PARAMS_NBAR']

    for i in range(0,par_n,4):
        # Loading values in the little-endian order
        a_row_temp[:4 * par_n:params['PARAMS_STRIPE_STEP']] = UINT16_TO_LE(i)
        a_row_temp[par_n:max_tmp:params['PARAMS_STRIPE_STEP']] += 1
        a_row_temp[2 * par_n:max_tmp:params['PARAMS_STRIPE_STEP']] += 1
        a_row_temp[3 * par_n:max_tmp:params['PARAMS_STRIPE_STEP']] += 1

        a_row = frombuffer(cipher.encrypt(a_row_temp), dtype=uint16).copy()
        a_row[:max_tmp] = LE_TO_UINT16(a_row[:max_tmp])

        sum_v = zeros((4,par_nbar), dtype=uint16)
        # Go through four lines with same s
        s_vec = s[:(par_nbar-1)*par_n + par_n]

        # Matrix vector multiplication
        a_row_0 = array(split(tile(a_row[:par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        a_row_1 = array(split(tile(a_row[par_n:2*par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        a_row_2 = array(split(tile(a_row[2*par_n:3*par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        a_row_3 = array(split(tile(a_row[3*par_n:4*par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)

        # Generate sum for each row
        sum_v[0] = sum(a_row_0[:par_nbar], axis=1)
        sum_v[1] = sum(a_row_1[:par_nbar], axis=1)
        sum_v[2] = sum(a_row_2[:par_nbar], axis=1)
        sum_v[3] = sum(a_row_3[:par_nbar], axis=1)

        # assign sum vectors to output intervals
        out[i * par_nbar   : i * par_nbar + par_nbar] += sum_v[0]
        out[(i+2) * par_nbar:(i+2) * par_nbar + par_nbar] += sum_v[2]
        out[(i+1) * par_nbar:(i+1) * par_nbar + par_nbar] += sum_v[1]
        out[(i+3) * par_nbar:(i+3) * par_nbar + par_nbar] += sum_v[3]

    return 1
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