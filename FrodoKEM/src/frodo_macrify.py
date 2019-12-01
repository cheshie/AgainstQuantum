from functools import reduce
from itertools import accumulate
from Crypto.Cipher import AES
from math import ceil
from numpy import zeros, uint16, frombuffer, uint8, uint64, array, sum, tile, \
    split, copyto, transpose, bitwise_and, array_split, hstack, repeat
from FrodoKEM.src.config import UINT16_TO_LE, LE_TO_UINT16

"""
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: matrix arithmetic functions used by the KEM
"""


class Frodo():
    @staticmethod
    def mul_add_as_plus_e(pm, out, s, e, seed_A):
        # Generate - and -multiply: generate matrix A(N x N) row - wise, multiply by s on the right.
        # Inputs: s, e(N x N_BAR)
        # Output: out = A * s + e(N x N_BAR)

        # Temporary values to make below lines shorter
        max_tmp = 4 * pm.PARAMS_N
        par_n = pm.PARAMS_N
        par_nbar = pm.PARAMS_NBAR

        # ALIGN_HEADER and FOOTER from config are used here
        a_row = zeros(4*pm.PARAMS_N,dtype=uint16)

        copyto(out, e[:par_n * par_nbar])

        # If USE_AES128_FOR_A defined
        a_row_temp = array(
            [UINT16_TO_LE(j - 1) if j % pm.PARAMS_STRIPE_STEP - 1 == 0 else 0
             for j in range(pm.PARAMS_N)] * 4,
            dtype=uint16
        )

        # Create new EVP cipher object and pass key from pk
        cipher = AES.new(seed_A[:16], AES.MODE_ECB)

        for i in range(0,par_n,4):
            # Loading values in the little-endian order
            a_row_temp[:4 * par_n:pm.PARAMS_STRIPE_STEP] = UINT16_TO_LE(i)
            a_row_temp[par_n:max_tmp:pm.PARAMS_STRIPE_STEP] += 1
            a_row_temp[2 * par_n:max_tmp:pm.PARAMS_STRIPE_STEP] += 1
            a_row_temp[3 * par_n:max_tmp:pm.PARAMS_STRIPE_STEP] += 1

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

    @staticmethod
    def mul_add_sa_plus_e(pm, out, s, e, seed_A):
        # Generate-and-multiply: generate matrix A (N x N) column-wise, multiply by s' on the left.
        # Inputs: s', e' (N_BAR x N)
        # Output: out = s'*A + e' (N_BAR x N)
        copyto(out, e[:pm.PARAMS_N*pm.PARAMS_NBAR])

        a_cols   = zeros(pm.PARAMS_N*pm.PARAMS_STRIPE_STEP,dtype=uint16)
        a_cols_t = zeros(pm.PARAMS_N*pm.PARAMS_STRIPE_STEP,dtype=uint16)
        a_cols_temp = zeros(pm.PARAMS_N*pm.PARAMS_STRIPE_STEP, dtype=uint16)

        # Create new EVP cipher object and pass key from pk
        cipher = AES.new(seed_A[:16], AES.MODE_ECB)

        # Loading values in the little - endian order
        a_cols_temp[:pm.PARAMS_N * pm.PARAMS_STRIPE_STEP:pm.PARAMS_STRIPE_STEP] =\
            array([UINT16_TO_LE(i) for i in range(pm.PARAMS_N)], dtype=uint16)

        for kk in range(0,pm.PARAMS_N,pm.PARAMS_STRIPE_STEP):
            # Go through A's columns, 8 (== PARAMS_STRIPE_STEP) columns at a time
            # Loading values in the little - endian order
            a_cols_temp[1:pm.PARAMS_N*pm.PARAMS_STRIPE_STEP:pm.PARAMS_STRIPE_STEP] = \
                array([UINT16_TO_LE(kk)] * pm.PARAMS_N, dtype=uint16)

            a_cols = frombuffer(cipher.encrypt(a_cols_temp), dtype=uint16).copy()

            # Transpose a_cols to have access to it in the column - major order.
            a_cols_t = transpose(a_cols.reshape((pm.PARAMS_N,a_cols.shape[0]//pm.PARAMS_N))).flatten()

            # Temporary values to make below lines shorter
            par_n    = pm.PARAMS_N
            par_st   = pm.PARAMS_STRIPE_STEP
            par_pl   = pm.PARAMS_PARALLEL

            for i in range(pm.PARAMS_NBAR):
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

    @staticmethod
    def mul_bs(pm, out, b, s):
        # Multiply by s on the right
        # Inputs: b(N_BAR x N), s(N x N_BAR)
        # Output: out = b * s(N_BAR x N_BAR)

        # Reference params for shorter lines
        pr_n = pm.PARAMS_N
        pr_nb = pm.PARAMS_NBAR
        pr_lq = pm.PARAMS_LOGQ

        # Calculate how many elements from s take, knowing that it should have size 40960
        # which is 5120 * 8 => meaning to be able to divide it into proper sub-vectors
        s_range = (pr_n * pr_nb * (pr_nb)) // pr_nb

        # Take range of elements from e vector
        out[:pr_nb ** 2 + pr_nb] = 0

        # array_split divides into n vectors, but what if we want to have vectors of n
        # len, and as many of them as array_split could divide vector into? Thus use of ceil(...)
        b_vec = hstack(tile(array_split(b[:s_range], ceil(s_range / pr_n)), pr_nb))
        # Split b vector into pr_n vectors and transpose them ('F').
        s_vec = tile(s[:pr_nb*pr_n + pr_n], pr_nb)

        out[:pr_nb ** 2 + pr_nb] += sum(array(split(b_vec * s_vec, pr_nb ** 2)), axis=1)
        out[:pr_nb ** 2 + pr_nb] = bitwise_and(out[:pr_nb ** 2 + pr_nb], ((1 << pr_lq) - 1))
    #

    @staticmethod
    def mul_add_sb_plus_e(pm, out, b, s, e):
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
        pr_n   = pm.PARAMS_N
        pr_nb  = pm.PARAMS_NBAR
        pr_lq  = pm.PARAMS_LOGQ

        # Calculate how many elements from s take, knowing that it should have size
        # r_n * pr_nb => meaning to be able to divide it into proper sub-vectors
        s_range = (pr_n * pr_nb * (pr_nb)) // pr_nb

        # Take range of elements from e vector
        out[:pr_nb**2 + pr_nb] = e[:pr_nb**2 + pr_nb]

        # array_split divides into n vectors, but what if we want to have vectors of n
        # len, and as many of them as array_split could divide vector into? Thus use of ceil(...)
        s_vec = hstack(tile(array_split(s[:s_range],ceil(s_range/pr_n)), pr_nb))
        # Split b vector into pr_n vectors and transpose them ('F').
        b_vec = tile(array(split(b, pr_n)).flatten('F')[:pr_n*pr_nb],pr_nb)

        out[:pr_nb**2 + pr_nb] += sum(array(split(s_vec * b_vec, pr_nb**2)),axis=1)
        out[:pr_nb**2 + pr_nb] = bitwise_and(out[:pr_nb**2 + pr_nb], ((1 << pr_lq) - 1))
    #

    @staticmethod
    def add(pm, out, a, b):
        # Add a and b
        # Inputs: a, b(N_BAR x N_BAR)
        # Output: c = a + b

        out[:pm.PARAMS_NBAR**2] = (a[:pm.PARAMS_NBAR**2] + b[:pm.PARAMS_NBAR**2]) \
                                         & ((1<<pm.PARAMS_LOGQ)-1)
    #

    @staticmethod
    def sub(pm, out, a, b):
        # Subs a and b
        # Inputs: a, b(N_BAR x N_BAR)
        # Output: c = a - b

        out[:pm.PARAMS_NBAR ** 2] = (a[:pm.PARAMS_NBAR ** 2] - b[:pm.PARAMS_NBAR ** 2]) \
                                           & ((1 << pm.PARAMS_LOGQ) - 1)
    #

    @staticmethod
    def key_encode(pm, out, invec):
        # Encoding
        par_eb = pm.PARAMS_EXTRACTED_BITS
        par_nb = pm.PARAMS_NBAR
        par_q  = pm.PARAMS_LOGQ

        # encoding parameters
        npieces_word = 8
        nwords = (par_nb ** 2) // 8
        mask = uint64((1<<par_eb) - 1)

        # Extract u8 vec from u16 vec and convert it to u64
        u8v = array(frombuffer(invec.tobytes(),dtype=uint8)[:nwords * par_eb + par_eb], dtype=uint64)

        # (8 * j) part
        temp = array(list(range(par_eb)) * (len(u8v)//par_eb), dtype=uint64) * 8
        temp = u8v << temp
        temp = array(reduce(lambda a,b: a | b, split(array(array_split(temp, len(temp) // par_eb)).flatten('F'), par_eb)), dtype=uint64)

        # Assign temp vector to out vector, doing some bit operations on the former
        temp = tile(split(temp, temp.shape[0]), npieces_word)
        temp = array([list(accumulate(x, lambda a,b: a >> uint64(par_eb))) for x in temp],dtype=uint16)
        out[:nwords * npieces_word] = (temp.flatten() & mask) << (par_q - par_eb)
    #

    @staticmethod
    def key_decode(pm, out, invec):
        # Decoding
        par_eb = pm.PARAMS_EXTRACTED_BITS
        par_nb = pm.PARAMS_NBAR
        par_q = pm.PARAMS_LOGQ

        npieces_word = 8
        nwords = (par_nb ** 2) // 8
        maskex = uint16((1 << par_eb) - 1)
        maskq  = uint16((1 << par_q) - 1)
        out.dtype = uint8 # instead of uint8 pos

        # temp = floor(in*2^{-11}=0.5)
        temp = split(((invec[:nwords * npieces_word] & maskq) +
                      (1 << (par_q - par_eb - 1))) >> (par_q - par_eb), npieces_word)

        # for each iteration of the top (i) loop arr has 8 elements, reduce them to 1
        templong = [reduce(lambda a,b: a | b, (x & maskex) << (par_eb * array(range(npieces_word)))) for x in temp]

        # repeat each element of templong for par_eb second inner loop, and repeat also second vector to match
        out[: nwords * par_eb] = \
                 (repeat(templong, par_eb) >> (8 * tile(range(par_eb), npieces_word))) & 0xFF

        # out dtype is back uint16
        out.dtype=uint16
    #
#