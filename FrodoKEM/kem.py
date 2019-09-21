from numpy import array, zeros, uint8, uint16, array_equal, uint64, ulonglong, frombuffer
#from numpymod import uint64, ulonglong
import secrets
import trace

trace.debug_mode = True
tlist = trace.tracelst
trace = trace.trace


def crypto_kem_keypair(pk, sk,shake, **params):
    # SHAKE IS DEFINED IN API_FRODO640 => its shake128

    # Generate the secret values, the seed for S and E, and
    #the seed for the seed for A.Add seed_A to the public key
    pk_seedA = pk
    pk_b     = pk[params['BYTES_SEED_A']:]
    sk_s     = sk
    sk_pk    = sk[params['CRYPTO_BYTES']:]
    sk_S     = sk[params['CRYPTO_BYTES']+params['CRYPTO_PUBLICKEYBYTES']:]
    sk_pkh   = sk[params['CRYPTO_BYTES']+params['CRYPTO_PUBLICKEYBYTES']+2*params['PARAMS_N']*params['PARAMS_NBAR']:]
    B = zeros(params['PARAMS_N']*params['PARAMS_NBAR'],dtype=uint16)
    S = zeros(2*params['PARAMS_N']*params['PARAMS_NBAR'],dtype=uint16)
    E = S[params['PARAMS_N']*params['PARAMS_NBAR']:]

    rcount = 2 * params['CRYPTO_BYTES'] + params['BYTES_SEED_A']
    #randomness =  array([randbyte for randbyte in secrets.token_bytes(rcount)], dtype=uint8)
    randomness = array([195, 42, 203, 181, 78, 183, 217, 4, 51, 106, 200, 157, 72, 124, 179, 143, 30, 209, 61, 196, 53, 59, 43, 115, 97, 172, 58, 185, 177, 163, 253, 110, 18, 55, 177, 14, 46, 108, 28, 107, 104, 211, 127, 74, 32, 175, 61, 154], dtype=uint8)

    randomness_s = randomness
    randomness_seedSE = randomness[params['CRYPTO_BYTES']:]
    randomness_z = randomness[2*params['CRYPTO_BYTES']:]
    shake_input_seedSE = zeros(1 + params['CRYPTO_BYTES'],dtype=uint8)

    # AFTER This function randomness_z is much shorter - has only  16 places. Why?
    #shake(pk_seedA, params['BYTES_SEED_A'], randomness_z, params['BYTES_SEED_A'])

    # Generate S and E, compute B = A*S + E. Generate A on-the-fly
    shake_input_seedSE[0] = 0x5F;

    # memcpy(dest, source, NUMBER-OF-BYTES) <== Carefully!
    for bt in range(params['CRYPTO_BYTES']):
        shake_input_seedSE[bt + 1] = randomness_seedSE[bt]

    # HEY IMPORTANT: THIS DOES NOT GET SHORTENED OUTSIDE FUNCTION!!!
    S_u8 = frombuffer(S.tobytes(), dtype=uint8).copy()
    sizeof_uint16 = 2

    shake(S_u8, 2*params['PARAMS_N']*params['PARAMS_NBAR']*sizeof_uint16, shake_input_seedSE, 1 + params['CRYPTO_BYTES'])
    S = frombuffer(S_u8.tobytes(), dtype=uint16)

    for i in range(2*params['PARAMS_N']*params['PARAMS_NBAR']):
        S[i] = UINT16_TO_LE(S[i])



    tlist("shake_input_seedSE", shake_input_seedSE)
    tlist("S", S)



    exit(0)
#


def crypto_kem_enc(ct, ss, pk, shake, **params):
    print(params['PARAMS_N'])


def crypto_kem_dec(ct, ss, pk, shake, **params):
    print(params['PARAMS_N'])