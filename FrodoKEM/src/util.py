from numpy import uint16, uint8

"""
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: additional functions for FrodoKEM
"""


def frodo_pack(out, outlen, invec, inlen, lsb):
    # Pack the input uint16 vector into a char output vector,
    # copying lsb bits from each input element.
    # If inlen * lsb / 8 > outlen, only outlen * 8 bits are copied.
    out[:outlen] = 0

    i = 0
    j = 0
    w = uint16(0)
    bits = uint8(0)

    while i < outlen and (j < inlen or ((j == inlen ) and (bits > 0))):
        # in: |        |        |********|********|
        #                       ^
        #                       j
        # w:  |    ****|
        #          ^
        #        bits
        #out: |**|**|**|**|**|**|**|**|* |
        #                             ^^
        #                             ib

        b = uint8(0) # Bits in out[i] already filled in
        while b < 8:
            nbits  = min(8-b, bits)
            mask   = (1 << nbits) - 1
            t      = (w >> uint8(bits - nbits)) & mask # the bits to copy from w to out
            out[i] = out[i] + (t << (8 - b - nbits))
            b    += nbits
            bits -= nbits
            w &= ~(mask << bits) # not strictly necessary, mostly for debugging

            if bits == 0:
                if j < inlen:
                    w = invec[j]
                    bits = lsb
                    j+= 1
                else:
                    break # The input vector is exhausted
            if b == 8: # out[i] is filled in
                i+= 1
#


def frodo_unpack(out, outlen, invec, inlen, lsb):
    # Unpack the input char vector into a uint16_t output vector, copying lsb bits
    # for each output element from input. outlen must be at least ceil(inlen * 8 / lsb).
    out[:outlen] = 0

    i = 0 # whole uint16_t already filled in
    j = 0 # whole bytes already copied
    w = uint8(0) # the leftover, not yet copied
    bits = uint8(0) # the number of lsb bits of w

    while i < outlen and (j < inlen or ((j == inlen ) and (bits > 0))):
        # in: |  |  |  |  |  |  |**|**|...
        #                       ^
        #                       j
        # w:  | *|
        #        ^
        #      bits
        #out: |   *****|   *****|   ***  |        |...
        #                       ^   ^
        #                       i   b

        b = uint8(0) # Bits in out[i] already filled in
        while b < lsb:
            nbits  = min(lsb - b, bits)
            mask   = uint16((1 << nbits) - 1)
            t      = (w >> uint8(bits - nbits)) & mask # the bits to copy from w to out
            out[i] = out[i] + (t << (lsb - b - nbits))
            b    += nbits
            bits -= nbits
            w &= ~(mask << bits) # not strictly necessary, mostly for debugging

            if bits == 0:
                if j < inlen:
                    w = invec[j]
                    bits = 8
                    j+= 1
                else:
                    break # The input vector is exhausted
        if b == lsb: # out[i] is filled in
            i+= 1
#