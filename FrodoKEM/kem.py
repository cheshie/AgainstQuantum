from numpy import array, uint8, array_equal
import secrets


def crypto_kem_keypair(pk, sk,shake, **params):
    # SHAKE IS DEFINED IN API_FRODO640 => its shake128
    pk_seedA = 0
    randomness_z = 2 * params['CRYPTO_BYTES']

    # Generate the secret values, the seed for S and E, and
    #the seed for the seed for A.Add seed_A to the public key
    rcount = 2 * params['CRYPTO_BYTES'] + params['BYTES_SEED_A']
    randomness =  array([randbyte for randbyte in secrets.token_bytes(rcount)], dtype=uint8)
    shake(pk, pk_seedA, params['BYTES_SEED_A'], randomness, randomness_z, params['BYTES_SEED_A'])
#


def crypto_kem_enc(ct, ss, pk, shake, **params):
    print(params['PARAMS_N'])


def crypto_kem_dec(ct, ss, pk, shake, **params):
    print(params['PARAMS_N'])