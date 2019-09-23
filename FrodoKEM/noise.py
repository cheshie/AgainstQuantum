from numpy import uint16
from warnings import filterwarnings, catch_warnings

filterwarnings('ignore')
with catch_warnings():
    filterwarnings('ignore', r'overflow')

"""
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: noise sampling functions
"""

def frodo_sample_n(s, n, **params):
    # Fills vector s with n samples from the noise distribution which requires 16 bits to sample.
    # The distribution is specified by its CDF.
    # Input: pseudo - random values(2 * n bytes) passed in s.The input
    # is overwritten by the output.
    for i in range(n):
        sample = uint16(0)
        prnd   = s[i] >> uint16(1) # Drop the least signifficant bit
        sign   = s[i] &  uint16(0x1) # Pick the LSB

        for j in range(params['CDF_TABLE_LEN'] - 1):
            # Constant time comparison: 1 if params['CDF_TABLE'][j] < s, 0 otherwise.Uses the fact that params['CDF_TABLE'][j] and s fit in 15 bits.
            try:
                sample += (params['CDF_TABLE'][j] - prnd) >> uint16(15)
            except RuntimeWarning as er:
                pass

        # Assuming that sign is either 0 or 1, flips sample iff sign = 1
        try:
            s[i] = ((-sign) ^ sample) + sign
        except RuntimeWarning as er:
            pass
