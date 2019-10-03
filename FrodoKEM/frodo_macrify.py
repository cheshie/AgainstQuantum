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


# TODO: Check datatypes here in params passed to this fun
def frodo_mul_add_sa_plus_e(out, s, e, seed_A, **params):
    # Generate-and-multiply: generate matrix A (N x N) column-wise, multiply by s' on the left.
    # Inputs: s', e' (N_BAR x N)
    # Output: out = s'*A + e' (N_BAR x N)
    #  TODO: Check if these arrays (out especially) is correct
    copyto(out, e[:params['PARAMS_N']*params['PARAMS_NBAR']])

    # printf("out: ");
    # for(int i=0; i<5120 ; i++)
    # {
    #     printf("%i, ",out[i]);
    # }
    # printf("\n\n");
    # printf("s: ");
    # for(int i=0; i<10304 ; i++)
    # {
    #     printf("%i, ",s[i]);
    # }
    # printf("\n\n");
    # printf("e: ");
    # for(int i=0; i<5184 ; i++)
    # {
    #     printf("%i, ",e[i]);
    # }
    # printf("\n\n");
    # exit(0);

    # NONE OF THESE IS CORRECT!!! Why?
    trc("out: ", len(out))
    trcl("out", out)
    trc("\n\n\ns: ", len(s))
    trcl("s", s)
    trc("\n\n\ne: ", len(e))
    trcl("e", e)
    exit()

    a_cols   = zeros(params['PARAMS_N']*params['PARAMS_STRIPE_STEP'],dtype=uint16)
    a_cols_t = zeros(params['PARAMS_N']*params['PARAMS_STRIPE_STEP'],dtype=uint16)
    a_cols_temp = zeros(params['PARAMS_N']*params['PARAMS_STRIPE_STEP'], dtype=uint16)

    # Create new EVP cipher object and pass key from pk
    cipher = AES.new(seed_A[:16], AES.MODE_ECB)

    # Loading values in the little - endian order
    a_cols_temp[:params['PARAMS_N'] * params['PARAMS_STRIPE_STEP']:params['PARAMS_STRIPE_STEP']] =\
        array([UINT16_TO_LE(i) for i in range(params['PARAMS_N'])], dtype=uint16)
    kk = 0

    # Go through A's columns, 8 (== PARAMS_STRIPE_STEP) columns at a time
    # Loading values in the little - endian order
    a_cols_temp[1:params['PARAMS_N']*params['PARAMS_STRIPE_STEP']:params['PARAMS_STRIPE_STEP']] = \
        array([UINT16_TO_LE(i) for i in range(0,params['PARAMS_N'] * params['PARAMS_STRIPE_STEP'],params['PARAMS_STRIPE_STEP'])], dtype=uint16)

    a_cols = frombuffer(cipher.encrypt(a_cols_temp), dtype=uint16).copy()

    # Transpose a_cols to have access to it in the column - major order.
    a_cols_t = LE_TO_UINT16(transpose(a_cols))

    # Temporary values to make below lines shorter
    max_tmp = 4 * params['PARAMS_N']
    par_n = params['PARAMS_N']
    par_nbar = params['PARAMS_NBAR']

    sum_v = zeros((params['PARAMS_PARALLEL'], par_nbar), dtype=uint16)
    # Go through four lines with same s
    s_vec = s[:(par_nbar - 1) * par_n + par_n]

    for p in range(0,params['PARAMS_STRIPE_STEP'],params['PARAMS_PARALLEL']):
        # Matrix vector multiplication
        a_cols_0 = array(split(tile(a_cols_t[p * par_n: p * par_n + par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        a_cols_1 = array(split(tile(a_cols_t[(p+1) * par_n: (p+1) * par_n + par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        a_cols_2 = array(split(tile(a_cols_t[(p+2) * par_n: (p+2) * par_n + par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)
        a_cols_3 = array(split(tile(a_cols_t[(p+3) * par_n: (p+3) * par_n + par_n], par_nbar) * s_vec, par_nbar), dtype=uint16)

        # Generate sum for each row
        sum_v[0] = sum(a_cols_0[:par_nbar], axis=1)
        sum_v[1] = sum(a_cols_1[:par_nbar], axis=1)
        sum_v[2] = sum(a_cols_2[:par_nbar], axis=1)
        sum_v[3] = sum(a_cols_3[:par_nbar], axis=1)

        # assign sum vectors to output intervals
        out[kk + p + 0: par_nbar + kk + p + 0] += sum_v[0]
        out[kk + p + 2: par_nbar + kk + p + 2] += sum_v[2]
        out[kk + p + 1: par_nbar + kk + p + 1] += sum_v[1]
        out[kk + p + 3: par_nbar + kk + p + 3] += sum_v[3]





    # Using vector intrinsics
    # TODO: MATRIX - VECTOR multip => CAN I use instead numpy????
    # for i in range(params['PARAMS_NBAR']):
    #     for k in range(0,params['PARAMS_STRIPE_STEP'],params['PARAMS_PARALLEL']):
    #         sum = empty(8 * params['PARAMS_PARALLEL'], dtype=uint32)
    #         # __m256i a[PARAMS_PARALLEL], b, acc[PARAMS_PARALLEL];
    #         a = empty(params['PARAMS_PARALLEL'], dtype=uint16)
    #         acc = zeros(params['PARAMS_PARALLEL'], dtype=uint16)
    #
    #         # Matrix - vector multiplication
    #         for j in range(0,params['PARAMS_N'],16):
    #             b = s[i*params['PARAMS_N'] + j]
    #             print("b: ",b)
    #             exit()
    #             a[0] = a_cols_t[(k+0)*params['PARAMS_N']+ j]
    #             a[0] += b
    #             acc[0] = a[0] + b
    #             a[1] = a_cols_t[(k + 1) * params['PARAMS_N'] + j]
    #             a[1] += b
    #             acc[1] = a[1] + acc[1]
    #             a[2] = a_cols_t[(k + 2) * params['PARAMS_N'] + j]
    #             a[2] += b
    #             acc[2] = a[2] + acc[2]
    #             a[3] = a_cols_t[(k + 3) * params['PARAMS_N'] + j]
    #             a[3] += b
    #             acc[3] = a[3] + acc[3]
    #
    #         sum[8 * 0] = acc[0]
    #         out[i*params['PARAMS_N'] + kk + k + 0] += \
    #             sum[8*0 + 0] + sum[8*0 + 1] + sum[8*0 + 2] + sum[8*0 + 3] + sum[8*0 + 4] + sum[8*0 + 5] + sum[8*0 + 6] + sum[8*0 + 7]
    #         sum[8 * 1] = acc[1]
    #         out[i * params['PARAMS_N'] + kk + k + 1] += \
    #             sum[8*1 + 0] + sum[8*1 + 1] + sum[8*1 + 2] + sum[8*1 + 3] + sum[8*1 + 4] + sum[8*1 + 5] + sum[8*1 + 6] + sum[8*1 + 7]
    #         sum[8 * 2] = acc[2]
    #         out[i * params['PARAMS_N'] + kk + k + 2] += \
    #             sum[8*2 + 0] + sum[8*2 + 1] + sum[8*2 + 2] + sum[8*2 + 3] + sum[8*2 + 4] + sum[8*2 + 5] + sum[8*2 + 6] + sum[8*2 + 7]
    #         sum[8 * 3] = acc[3]
    #         out[i * params['PARAMS_N'] + kk + k + 2] += \
    #             sum[8*3 + 0] + sum[8*3 + 1] + sum[8*3 + 2] + sum[8*3 + 3] + sum[8*3 + 4] + sum[8*3 + 5] + sum[8*3 + 6] + sum[8*3 + 7]


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