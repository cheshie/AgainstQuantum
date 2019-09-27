from numpy import zeros, uint16, frombuffer, uint32, uint8, array, sum, tile, split
import trace

trace.debug_mode = True
tlist = trace.tracelst
trace = trace.trace
"""
* FrodoKEM: Learning with Errors Key Encapsulation
*
* Abstract: additional functions for FrodoKEM
"""

def frodo_pack(out, outlen, invec, inlen, lsb):
    # Pack the input uint16 vector into a char output vector,
    # copying lsb bits from each input element.
    # If inlen * lsb / 8 > outlen, only outlen * 8 bits are copied.
    out[outlen:] = 0

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
            mask   = uint16((1 << nbits) - 1)
            t      = uint8((w >> (bits - nbits)) & mask) # the bits to copy from w to out
            trace("out[i]: ",(t << (8 - b - nbits)))
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