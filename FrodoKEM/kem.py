from numpy import array, uint8, array_equal
from numpymod import uint64, ulonglong
import secrets


def crypto_kem_keypair(pk, sk,shake, **params):
    # SHAKE IS DEFINED IN API_FRODO640 => its shake128
    pk_seedA = pk
    randomness_z = 2 * params['CRYPTO_BYTES']

    # Generate the secret values, the seed for S and E, and
    #the seed for the seed for A.Add seed_A to the public key
    rcount = 2 * params['CRYPTO_BYTES'] + params['BYTES_SEED_A']
    #randomness =  array([randbyte for randbyte in secrets.token_bytes(rcount)], dtype=uint8)
    randomness = array([195, 42, 203, 181, 78, 183, 217, 4, 51, 106, 200, 157, 72, 124, 179, 143, 30, 209, 61, 196, 53, 59, 43, 115, 97, 172, 58, 185, 177, 163, 253, 110, 18, 55, 177, 14, 46, 108, 28, 107, 104, 211, 127, 74, 32, 175, 61, 154], dtype=uint8)

    randomness_s = randomness
    randomness_seedSE = randomness[params['CRYPTO_BYTES']:]
    randomness_z = randomness[2*params['CRYPTO_BYTES']:]
    # shake_input_seedSE[1 + params['CRYPTO_BYTES']]  declare numpy array here

    #TODO: eliminate pk and index of pk. Instead pass part of array that is needed
    shake(pk_seedA, params['BYTES_SEED_A'], randomness_z, params['BYTES_SEED_A'])
#


def crypto_kem_enc(ct, ss, pk, shake, **params):
    print(params['PARAMS_N'])


def crypto_kem_dec(ct, ss, pk, shake, **params):
    print(params['PARAMS_N'])