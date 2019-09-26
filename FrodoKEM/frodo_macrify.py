import config
from numpy import zeros, uint16, frombuffer, uint32, uint8, array, sum
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
    a_row_temp = array(
        [UINT16_TO_LE(j - 1) if j % params['PARAMS_STRIPE_STEP'] - 1 == 0 else 0
         for j in range(params['PARAMS_N'])] * 4,
        dtype=uint16
    )

    # Create new EVP cipher object and pass key from pk
    cipher = AES.new(seed_A[:16], AES.MODE_ECB)

    #TODO
    # TODO: All these LOOPS - its very uneffective!!!!
    #TODO

    # for j in range(0,params['PARAMS_N'],params['PARAMS_STRIPE_STEP']):
    #     a_row_temp[j + 1 + 0 * params['PARAMS_N']] = UINT16_TO_LE(j)
    #     a_row_temp[j + 1 + 1 * params['PARAMS_N']] = UINT16_TO_LE(j)    # Loading values in the little-endian order
    #     a_row_temp[j + 1 + 2 * params['PARAMS_N']] = UINT16_TO_LE(j)
    #     a_row_temp[j + 1 + 3 * params['PARAMS_N']] = UINT16_TO_LE(j)
    max_tmp = 4 * params['PARAMS_N']

    for i in range(0,params['PARAMS_N'],4):
        # Loading values in the little-endian order
        a_row_temp[:4 * params['PARAMS_N']:params['PARAMS_STRIPE_STEP']] = UINT16_TO_LE(i)
        a_row_temp[    params['PARAMS_N']:max_tmp:params['PARAMS_STRIPE_STEP']] += 1
        a_row_temp[2 * params['PARAMS_N']:max_tmp:params['PARAMS_STRIPE_STEP']] += 1
        a_row_temp[3 * params['PARAMS_N']:max_tmp:params['PARAMS_STRIPE_STEP']] += 1

        #
        # for j in range(0, params['PARAMS_N'], params['PARAMS_STRIPE_STEP']):
        #     a_row_temp[j + 0 * params['PARAMS_N']] = UINT16_TO_LE(i+0)
        #     a_row_temp[j + 1 * params['PARAMS_N']] = UINT16_TO_LE(i+1)  # Loading values in the little-endian order
        #     a_row_temp[j + 2 * params['PARAMS_N']] = UINT16_TO_LE(i+2)
        #     a_row_temp[j + 3 * params['PARAMS_N']] = UINT16_TO_LE(i+3)

        a_row = frombuffer(cipher.encrypt(a_row_temp), dtype=uint16).copy()
        a_row[:max_tmp] = LE_TO_UINT16(a_row[:max_tmp])

        par_n = params['PARAMS_N']

        sum_v = zeros(4, dtype=uint16)

        for k in range(params['PARAMS_NBAR']):
            # Matrix vector multiplication
            s_vec = s[k * params['PARAMS_N']:k * params['PARAMS_N'] + params['PARAMS_N']]

            # Go through four lines with same s
            sum_v[0] = sum(a_row[:par_n] * s_vec)
            sum_v[1] = sum(a_row[par_n:2 * par_n] * s_vec)
            sum_v[2] = sum(a_row[2 * par_n:3 * par_n] * s_vec)
            sum_v[3] = sum(a_row[3 * par_n:4 * par_n] * s_vec)

            # for j in range(params['PARAMS_N']):
            #
            #     sum[0] += a_row[0 * params['PARAMS_N'] + j] * s[k*params['PARAMS_N'] + j] # Go through lines with the same s
            #     sum[1] += a_row[1 * params['PARAMS_N'] + j] * s[k*params['PARAMS_N'] + j]
            #     sum[2] += a_row[2 * params['PARAMS_N'] + j] * s[k*params['PARAMS_N'] + j]
            #     sum[3] += a_row[3 * params['PARAMS_N'] + j] * s[k*params['PARAMS_N'] + j]

            #out[ i * params['PARAMS_NBAR']   : i * params['PARAMS_NBAR'] + params['PARAMS_NBAR']] += sum_v[0]
            #out[(i+2) * params['PARAMS_NBAR']:(i+2) * params['PARAMS_NBAR'] + params['PARAMS_NBAR']] += sum_v[2]
            #out[(i+1) * params['PARAMS_NBAR']:(i+1) * params['PARAMS_NBAR'] + params['PARAMS_NBAR']] += sum_v[1]
            #out[(i+3) * params['PARAMS_NBAR']:(i+3) * params['PARAMS_NBAR'] + params['PARAMS_NBAR']] += sum_v[3]

            # out[(i + 0) * params['PARAMS_NBAR'] + k] += sum_v[0]
            # out[(i + 2) * params['PARAMS_NBAR'] + k] += sum_v[2]
            # out[(i + 1) * params['PARAMS_NBAR'] + k] += sum_v[1]
            # out[(i + 3) * params['PARAMS_NBAR'] + k] += sum_v[3]

    # trace(f"s, size({len(s)}): \n\n")
    # tlist("s", s)
    # trace(f"e, size({len(e)}): \n\n")
    # tlist("e", e)

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