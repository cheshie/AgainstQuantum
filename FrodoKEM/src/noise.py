from numpy import uint16, repeat, tile, split, sum

"""
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: noise sampling functions
"""


def frodo_sample_n(s, n, pm):
    # Fills vector s with n samples from the noise distribution which requires 16 bits to sample.
    # The distribution is specified by its CDF.
    # Input: pseudo - random values(2 * n bytes) passed in s.The input
    # is overwritten by the output.
    cdf_tab = pm.CDF_TABLE[:pm.CDF_TABLE_LEN - 1]

    # No need to compare with the last value.
    # Constant time comparison: 1 if CDF_TABLE[j] < s, 0 otherwise.
    # Uses the fact that CDF_TABLE[j] and s fit in 15 bits.
    sample = split(tile(cdf_tab, n) - repeat(s[:n] >> 1, pm.CDF_TABLE_LEN - 1) >> 15, n)
    sample = sum(sample, axis=1)

    # Assuming that sign is either 0 or 1, flips sample iff sign = 1
    s[:n] = uint16((-(s[:n] & 0x1) ^ sample[:n]) + (s[:n] & 0x1))
#