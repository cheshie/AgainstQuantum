import config
# TODO: Clean up these imports and split them into lines
from numpy import zeros, uint16, frombuffer, uint32, uint8, array, sum, tile, split, copyto, transpose, empty
from Crypto.Cipher import AES
from config import UINT16_TO_LE, LE_TO_UINT16
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
        # https: // docs.scipy.org / doc / numpy / reference / generated / numpy.ndarray.flatten.html
        # TODO: FORTRAN STYLE?
        a_cols_t = transpose(a_cols.reshape((params['PARAMS_N'],a_cols.shape[0]//params['PARAMS_N']))).flatten()

        # Temporary values to make below lines shorter
        par_n    = params['PARAMS_N']
        par_st   = params['PARAMS_STRIPE_STEP']
        par_pl   = params['PARAMS_PARALLEL']

        for i in range(params['PARAMS_NBAR']):
            s_vec = array(s[i * par_n:i * par_n + par_n], dtype=uint16)

            a_cols_0_temp = array(split(a_cols_t[:par_st * par_n + par_n], par_st))[range(0,par_st,par_pl)].flatten()
            trc("a_cols: ",len(a_cols_0_temp))
            a_cols_0 = array(split(a_cols_0_temp * tile(s_vec,par_st//par_pl), par_st//par_pl),dtype = uint16)

            a_cols_1_temp = array(split(a_cols_t[par_n:(par_st+1) * par_n + par_n], par_st))[range(0, par_st, par_pl)].flatten()
            trc("a_cols: ", len(a_cols_1_temp))
            #a_cols_1 = array(split(a_cols_1_temp * tile(s_vec, par_st // par_pl), par_st // par_pl), dtype=uint16)

            a_cols_2_temp = array(split(a_cols_t[2 * par_n:(par_st+2) * par_n + par_n], par_st))[range(0, par_st, par_pl)].flatten()
            trc("a_cols: ", len(a_cols_2_temp))
            a_cols_2 = array(split(a_cols_2_temp * tile(s_vec, par_st // par_pl), par_st // par_pl), dtype=uint16)

            a_cols_3_temp = array(split(a_cols_t[3 * par_n:(par_st+3) * par_st * par_n + par_n], par_st))[range(0, par_st, par_pl)].flatten()
            a_cols_3 = array(split(a_cols_3_temp * tile(s_vec, par_st // par_pl), par_st // par_pl), dtype=uint16)

            sum_0 = array(sum(a_cols_0[:par_n], axis=1), dtype=uint16)
            sum_1 = array(sum(a_cols_1[:par_n], axis=1), dtype=uint16)
            sum_2 = array(sum(a_cols_2[:par_n], axis=1), dtype=uint16)
            sum_3 = array(sum(a_cols_3[:par_n], axis=1), dtype=uint16)

            out[i * par_n + kk + range(0,par_st,par_pl) + 0] += sum_0
            out[i * par_n + kk + range(0,par_st,par_pl) + 2] += sum_2
            out[i * par_n + kk + range(0,par_st,par_pl) + 1] += sum_1
            out[i * par_n + kk + range(0,par_st,par_pl) + 3] += sum_3

            exit()

            for k in range(0,params['PARAMS_STRIPE_STEP'], params['PARAMS_PARALLEL']):
                sum_v = zeros(params['PARAMS_PARALLEL'],dtype=uint16)

                #sum_v[0] += sum(s_vec * a_cols_t[(k) * par_n:(k) * par_n + par_n])
                #sum_v[1] += sum(s_vec * a_cols_t[(k+1) * par_n:(k+1) * par_n + par_n])
                #sum_v[2] += sum(s_vec * a_cols_t[(k + 2) * par_n:(k + 2) * par_n + par_n])
                #sum_v[3] += sum(s_vec * a_cols_t[(k + 3) * par_n:(k + 3) * par_n + par_n])
                # for j in range(params['PARAMS_N']):
                #     # matrix vector multip
                #     # sum[0] += sp * a_cols_t[(k)*par_n+j]
                #     sum[1] += sp * a_cols_t[(k+1) * par_n + j]
                #     sum[2] += sp * a_cols_t[(k+2) * par_n + j]
                #     sum[3] += sp * a_cols_t[(k+3) * par_n + j]

                trc("sum: ",sum_v[0])
                out[i * par_n + kk + k + 0] += sum_v[0]
                out[i * par_n + kk + k + 2] += sum_v[2]
                out[i * par_n + kk + k + 1] += sum_v[1]
                out[i * par_n + kk + k + 3] += sum_v[3]


            #print(sum_v[0])
            #print(sum_a)
            exit()

        trc("\n\n\nout: ", len(out))
        trcl("out", out)
        exit()


        # sum_v = zeros((params['PARAMS_PARALLEL'], par_nbar), dtype=uint16)
        # # Go through four lines with same s
        # s_vec = s[:(par_nbar - 1) * par_n + par_n]
        #
        # for k in range(0,params['PARAMS_STRIPE_STEP'],params['PARAMS_PARALLEL']):
        #     # Matrix vector multiplication
        #     a_cols_0 = array(split(tile(a_cols_t[k * par_n: k * par_n + par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        #     a_cols_1 = array(split(tile(a_cols_t[(k+1) * par_n: (k+1) * par_n + par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        #     a_cols_2 = array(split(tile(a_cols_t[(k+2) * par_n: (k+2) * par_n + par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        #     a_cols_3 = array(split(tile(a_cols_t[(k+3) * par_n: (k+3) * par_n + par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        #
        #     # Generate sum for each row
        #     sum_v[0] = sum(a_cols_0[:par_nbar], axis=1)
        #     sum_v[1] = sum(a_cols_1[:par_nbar], axis=1)
        #     sum_v[2] = sum(a_cols_2[:par_nbar], axis=1)
        #     sum_v[3] = sum(a_cols_3[:par_nbar], axis=1)
        #
        #     # trcl("SUM", sum_v)
        #
        #     # assign sum vectors to output intervals
        #     out[kk + k + 0: par_nbar + kk + k + 0] += sum_v[0]
        #     trcl("out: ",out[kk + k + 0: par_nbar + kk + k + 0])
        #     exit()
        #     out[kk + k + 2: par_nbar + kk + k + 2] += sum_v[2]
        #     out[kk + k + 1: par_nbar + kk + k + 1] += sum_v[1]
        #     out[kk + k + 3: par_nbar + kk + k + 3] += sum_v[3]

    # NONE OF THESE IS CORRECT!!! Why?
    trc("out: ", len(out))
    trcl("out", out)
    trc("\n\n\ns: ", len(s))
    trcl("s", s)
    trc("\n\n\ne: ", len(e))
    trcl("e", e)
    exit()

    print("out: ",len(out))
    print("out: ",out)

    exit()
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