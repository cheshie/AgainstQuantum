from numpy import empty, uint64, uint8

global SHAKE128_RATE
global SHAKE256_RATE
SHAKE128_RATE = 168
SHAKE256_RATE = 136


def shake128(output_start, output, outlen, input_start, input, inlen):
    s = empty(25, dtype=uint64)
    t = empty(SHAKE128_RATE, dtype=uint8)
    nblocks = outlen / SHAKE128_RATE

    # Absorb input
    keccak_absorb()

    # Squeeze output
    keccak_squeezeblocks()

    output += nblocks*SHAKE128_RATE
    outlen -= nblocks*SHAKE128_RATE

    if outlen:
        keccak_squeezeblocks()
        for i in range(outlen):
            output[i] = t[i]
#

def keccak_absorb():
    # possible implementation:
    #https: // github.com / zjtone / keccak - python / blob / master / Keccak.py
    # This one is python3 wrapper written in c and doesn't match my needs: https://pypi.org/project/pysha3/#downloads
    pass

def keccak_squeezeblocks():
    pass


