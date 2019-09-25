import config
from numpy import zeros, uint16, frombuffer, uint32, uint8, array
from Crypto.Cipher import AES
from config import UINT16_TO_LE, LE_TO_UINT16
import trace

trace.debug_mode = True
tlist = trace.tracelst
trace = trace.trace

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

    out = e.copy()

    # If USE_AES128_FOR_A defined
    a_row_temp = zeros(4*params['PARAMS_N'], dtype=uint16)

    # Create new EVP cipher object and pass key from pk
    cipher = AES.new(seed_A[:16], AES.MODE_ECB)

    #TODO
    # TODO: All these LOOPS - its very uneffective!!!!
    #TODO

    # THIS WRONG => HOW TO MAKE IT RIGHT AND FAST??
    # tmp = params['PARAMS_N']    # Loading values in the little-endian order
    # a_row_temp[1:tmp:params['PARAMS_STRIPE_STEP']] =\
    # a_row_temp[tmp + 1:2 * tmp:params['PARAMS_STRIPE_STEP']] =\
    # a_row_temp[2 * tmp + 1:3 * tmp:params['PARAMS_STRIPE_STEP']] =\
    # a_row_temp[3 * tmp + 1:4 * tmp:params['PARAMS_STRIPE_STEP']] = UINT16_TO_LE(tmp)

    for j in range(0,params['PARAMS_N'],params['PARAMS_STRIPE_STEP']):
        a_row_temp[j + 1 + 0 * params['PARAMS_N']] = UINT16_TO_LE(j)
        a_row_temp[j + 1 + 1 * params['PARAMS_N']] = UINT16_TO_LE(j)    # Loading values in the little-endian order
        a_row_temp[j + 1 + 2 * params['PARAMS_N']] = UINT16_TO_LE(j)
        a_row_temp[j + 1 + 3 * params['PARAMS_N']] = UINT16_TO_LE(j)

    for i in range(0,params['PARAMS_N'],4):
        for j in range(0, params['PARAMS_N'], params['PARAMS_STRIPE_STEP']):
            a_row_temp[j + 0 * params['PARAMS_N']] = UINT16_TO_LE(i+0)
            a_row_temp[j + 1 * params['PARAMS_N']] = UINT16_TO_LE(i+1)  # Loading values in the little-endian order
            a_row_temp[j + 2 * params['PARAMS_N']] = UINT16_TO_LE(i+2)
            a_row_temp[j + 3 * params['PARAMS_N']] = UINT16_TO_LE(i+3)

        a_row = frombuffer(cipher.encrypt(a_row_temp), dtype=uint16).copy()

        for k in range(4*params['PARAMS_N']):
            a_row[k] = LE_TO_UINT16(a_row[k])

        for k in range(params['PARAMS_NBAR']):
            sum = zeros(4, dtype=uint16)
            for j in range(params['PARAMS_N']):
                # Matrix vector multiplication
                sp = s[k*params['PARAMS_N'] + j]
                sum[0] += a_row[0 * params['PARAMS_N'] + j] * sp # Go through lines with the same s
                sum[1] += a_row[1 * params['PARAMS_N'] + j] * sp
                sum[2] += a_row[2 * params['PARAMS_N'] + j] * sp
                sum[3] += a_row[3 * params['PARAMS_N'] + j] * sp

            out[(i + 0) * params['PARAMS_NBAR'] + k] += sum[0]
            out[(i + 2) * params['PARAMS_NBAR'] + k] += sum[2]
            out[(i + 1) * params['PARAMS_NBAR'] + k] += sum[1]
            out[(i + 3) * params['PARAMS_NBAR'] + k] += sum[3]

    # trace(f"s, size({len(s)}): \n\n")
    # tlist("s", s)
    trace(f"e, size({len(e)}): \n\n")
    tlist("e", e)

    trace(f"out, size({len(out)}): \n\n")
    tlist("out", out)
    exit(0)
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