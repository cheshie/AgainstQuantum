import config
# TODO: Clean up these imports and split them into lines
from numpy import zeros, uint16, frombuffer, uint32, uint8, array, sum, tile, split, copyto, transpose, empty, bitwise_and, array_split, hstack
from Crypto.Cipher import AES
from config import UINT16_TO_LE, LE_TO_UINT16
from math import ceil
import trace

trace.debug_mode = True
trcl = trace.tracelst
trc = trace.trace

"""
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: matrix arithmetic functions used by the KEM
"""

# TODO: Compile it with optimalization for AVX for python - with
#  Virtual Env and so. There was an article about it, makes code 20x faster


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


def frodo_mul_add_sa_plus_e(out, s, e, seed_A, **params):
    # Generate-and-multiply: generate matrix A (N x N) column-wise, multiply by s' on the left.
    # Inputs: s', e' (N_BAR x N)
    # Output: out = s'*A + e' (N_BAR x N)
    copyto(out, e[:params['PARAMS_N']*params['PARAMS_NBAR']])

    a_cols   = zeros(params['PARAMS_N']*params['PARAMS_STRIPE_STEP'],dtype=uint16)
    a_cols_t = zeros(params['PARAMS_N']*params['PARAMS_STRIPE_STEP'],dtype=uint16)
    a_cols_temp = zeros(params['PARAMS_N']*params['PARAMS_STRIPE_STEP'], dtype=uint16)

    # Create new EVP cipher object and pass key from pk
    cipher = AES.new(seed_A[:16], AES.MODE_ECB)

    # Loading values in the little - endian order
    a_cols_temp[:params['PARAMS_N'] * params['PARAMS_STRIPE_STEP']:params['PARAMS_STRIPE_STEP']] =\
        array([UINT16_TO_LE(i) for i in range(params['PARAMS_N'])], dtype=uint16)

    for kk in range(0,params['PARAMS_N'],params['PARAMS_STRIPE_STEP']):
        # Go through A's columns, 8 (== PARAMS_STRIPE_STEP) columns at a time
        # Loading values in the little - endian order
        a_cols_temp[1:params['PARAMS_N']*params['PARAMS_STRIPE_STEP']:params['PARAMS_STRIPE_STEP']] = \
            array([UINT16_TO_LE(kk)] * params['PARAMS_N'], dtype=uint16)

        a_cols = frombuffer(cipher.encrypt(a_cols_temp), dtype=uint16).copy()

        # Transpose a_cols to have access to it in the column - major order.
        a_cols_t = transpose(a_cols.reshape((params['PARAMS_N'],a_cols.shape[0]//params['PARAMS_N']))).flatten()

        # Temporary values to make below lines shorter
        par_n    = params['PARAMS_N']
        par_st   = params['PARAMS_STRIPE_STEP']
        par_pl   = params['PARAMS_PARALLEL']

        for i in range(params['PARAMS_NBAR']):
            s_vec = array(s[i * par_n:i * par_n + par_n], dtype=uint16)
            new_a_cols_t = array(split(a_cols_t, par_st))

            a_cols_0_temp = new_a_cols_t[range(0,par_st,par_pl)].flatten()
            a_cols_0 = array(split(a_cols_0_temp * tile(s_vec,par_st//par_pl), par_st//par_pl),dtype = uint16)

            a_cols_1_temp = new_a_cols_t[range(1,par_st,par_pl)].flatten()
            a_cols_1 = array(split(a_cols_1_temp * tile(s_vec, par_st // par_pl), par_st // par_pl), dtype=uint16)

            a_cols_2_temp = new_a_cols_t[range(2,par_st,par_pl)].flatten()
            a_cols_2 = array(split(a_cols_2_temp * tile(s_vec, par_st // par_pl), par_st // par_pl), dtype=uint16)

            a_cols_3_temp = new_a_cols_t[range(3,par_st,par_pl)].flatten()
            a_cols_3 = array(split(a_cols_3_temp * tile(s_vec, par_st // par_pl), par_st // par_pl), dtype=uint16)

            indx = i * par_n + kk
            out[range(indx + 0,indx + par_st + 0, par_pl)] += sum(a_cols_0[:par_n], axis=1)
            out[range(indx + 2,indx + par_st + 2, par_pl)] += sum(a_cols_2[:par_n], axis=1)
            out[range(indx + 1,indx + par_st + 1, par_pl)] += sum(a_cols_1[:par_n], axis=1)
            out[range(indx + 3,indx + par_st + 3, par_pl)] += sum(a_cols_3[:par_n], axis=1)

    return 1
#


def frodo_mul_bs(out, b, s):
    pass
#


def frodo_mul_add_sb_plus_e(out, b, s, e, **params):
    # Multiply by s on the left
    # Inputs: b(N x N_BAR), s(N_BAR x N), e(N_BAR x N_BAR)
    # Output: out = s * b + e(N_BAR x N_BAR)

    # The following code does exactly the same as this in comments, but with no loops
    # Leaving for reference
    # for k in range(pr_nb):
    #     out[k * pr_nb: k * pr_nb + pr_nb] = e[k * pr_nb: k * pr_nb + pr_nb]
    #
    #     out[k * pr_nb: k * pr_nb + pr_nb] += sum(split(tile(s[k * pr_n:k * pr_n + pr_n], pr_nb)
    #                                                    * array(split(b, pr_n)).flatten('F')[:pr_n * pr_nb], pr_nb),
    #                                              axis=1)
    #
    #     out[k * pr_nb: k * pr_nb + pr_nb] = bitwise_and(out[k * pr_nb: k * pr_nb + pr_nb], ((1 << pr_lq) - 1))
    #

    # Reference params for shorter lines
    pr_n   = params['PARAMS_N']
    pr_nb  = params['PARAMS_NBAR']
    pr_lq  = params['PARAMS_LOGQ']

    # Calculate how many elements from s take, knowing that it should have size 40960
    # which is 5120 * 8 => meaning to be able to divide it into proper sub-vectors
    s_range = (pr_n * pr_nb * (pr_nb)) // pr_nb

    out[:pr_nb**2 + pr_nb] = e[:pr_nb**2 + pr_nb]

    # array_split divides into n vectors, but what if we want to have vectors of n
    # len, and as many of them as array_split could divide vector into? Thus use of ceil(...)
    s_vec = hstack(tile(array_split(s[:s_range],ceil(s_range/pr_n)), pr_nb))
    # Split b vector into pr_n vectors and transpose them ('F').
    b_vec = tile(array(split(b, pr_n)).flatten('F')[:pr_n*pr_nb],pr_nb)

    out[:pr_nb**2 + pr_nb] += sum(array(split(s_vec * b_vec, pr_nb**2)),axis=1)
    out[:pr_nb**2 + pr_nb] = bitwise_and(out[:pr_nb**2 + pr_nb], ((1 << pr_lq) - 1))
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