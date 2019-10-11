from numpy import array, zeros, uint8, uint16, array_equal, uint64, ulonglong, frombuffer, empty, copyto
from config import LE_TO_UINT16, UINT16_TO_LE
from noise import frodo_sample_n
from frodo_macrify import frodo_mul_add_as_plus_e, frodo_mul_add_sa_plus_e, frodo_mul_add_sb_plus_e
from util import frodo_pack, frodo_unpack
import secrets
import trace

trace.debug_mode = True
trcl = trace.tracelst
trc = trace.trace

# TODO: About changing Numpy arrays type, you dont need to frombuffer().copy() and so!
# TODO: What you need is array.dtype = uint8
# TODO: https://stackoverflow.com/questions/4389517/in-place-type-conversion-of-a-numpy-array/4396247#4396247

#TODO: For tests, you must change empty() to zeros() in test_kem.py
def crypto_kem_keypair(pk, sk, shake, **params):
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
    shake(pk_seedA, params['BYTES_SEED_A'], randomness_z, params['BYTES_SEED_A'])

    # Generate S and E, compute B = A*S + E. Generate A on-the-fly
    shake_input_seedSE[0] = 0x5F

    # memcpy(dest, source, NUMBER-OF-BYTES) <== Carefully!
    shake_input_seedSE[1:params['CRYPTO_BYTES']+1] = randomness_seedSE[:params['CRYPTO_BYTES']]

    # HEY IMPORTANT: THIS DOES NOT GET SHORTENED OUTSIDE FUNCTION!!!
    S_u8 = frombuffer(S.tobytes(), dtype=uint8).copy()
    sizeof_uint16 = 2

    shake(S_u8,2*params['PARAMS_N']*params['PARAMS_NBAR']*sizeof_uint16,
          shake_input_seedSE, 1 + params['CRYPTO_BYTES'])

    S = frombuffer(S_u8.tobytes(), dtype=uint16).copy()
    E = S[params['PARAMS_N'] * params['PARAMS_NBAR']:]

    for i in range(2*params['PARAMS_N']*params['PARAMS_NBAR']):
        S[i] = UINT16_TO_LE(S[i])


    frodo_sample_n(S, params['PARAMS_N']*params['PARAMS_NBAR'], **params)
    frodo_sample_n(E, params['PARAMS_N']*params['PARAMS_NBAR'], **params)


    frodo_mul_add_as_plus_e(B, S, E, pk, **params)


    # Encode the second part of the public key
    frodo_pack(pk_b, params['CRYPTO_PUBLICKEYBYTES'] - params['BYTES_SEED_A'],
               B, params['PARAMS_N']*params['PARAMS_NBAR'], params['PARAMS_LOGQ'])


    # Add s, pk and S to the secret key
    sk_s[:params['CRYPTO_BYTES']] = randomness_s[:params['CRYPTO_BYTES']]
    # This is safe - sk_pk does get copy of range of els in pk
    sk_pk[:params['CRYPTO_PUBLICKEYBYTES']] = pk[:params['CRYPTO_PUBLICKEYBYTES']]


    #Convert uint16 to little endian
    S[:params['PARAMS_N']*params['PARAMS_NBAR']] =\
        UINT16_TO_LE(S[:params['PARAMS_N']*params['PARAMS_NBAR']])

    sk_S[:2 * params['PARAMS_N']*params['PARAMS_NBAR']] =\
        frombuffer(S[:params['PARAMS_N']*params['PARAMS_NBAR']].tobytes(),dtype=uint8).copy()


    # Add H(pk) to the secret key
    shake(sk_pkh, params['BYTES_PKHASH'], pk, params['CRYPTO_PUBLICKEYBYTES'])

    # Cleanup
    S[:params['PARAMS_N']*params['PARAMS_NBAR']] = 0
    E[:params['PARAMS_N']*params['PARAMS_NBAR']] = 0
    randomness[:2*params['CRYPTO_BYTES']] = 0
    shake_input_seedSE[:1 + params['CRYPTO_BYTES']] = 0

    return 0
#


def crypto_kem_enc(ct, ss, pk, shake, **params):
    # FrodoKEM's key encapsulation
    pk_seedA = pk
    pk_b     = pk[params['BYTES_SEED_A']:]
    ct_c1    = ct
    ct_c2    = ct[:(params['PARAMS_LOGQ'] * params['PARAMS_N'] * params['PARAMS_NBAR'])//8]
    B = zeros(params['PARAMS_N'] * params['PARAMS_NBAR'], dtype=uint16)
    V = zeros(params['PARAMS_NBAR'] ** 2, dtype=uint16) # Contains secret data
    C = zeros(params['PARAMS_NBAR'] ** 2, dtype=uint16)

    Bp = zeros(params['PARAMS_N'] * params['PARAMS_NBAR'], dtype=uint16)
    Sp = zeros((2 * params['PARAMS_N'] + params['PARAMS_NBAR']) * params['PARAMS_NBAR'], dtype=uint16) # contains secret data
    Ep = Sp[params['PARAMS_N'] * params['PARAMS_NBAR']:] # Contains secret data
    Epp= Sp[2 * params['PARAMS_N'] * params['PARAMS_NBAR']:] # Contains secret data
    # TODO: Empty here, it might be needed to change into zeros for tests
    G2in = empty(params['BYTES_PKHASH']+params['BYTES_MU'], dtype=uint8) # Contains secret data via mu
    pkh  = G2in
    mu   = G2in[params['BYTES_PKHASH']:] # Contains secret data
    G2out= empty(2 * params['CRYPTO_BYTES'], dtype=uint8) # Contains secret data
    seedSE = G2out # Contains secret data
    k = G2out[params['CRYPTO_BYTES']:] # Contains secret data
    Fin    = empty(params['CRYPTO_CIPHERTEXTBYTES'] + params['CRYPTO_BYTES'], dtype=uint8) # Contains secret data via Fin_k
    Fin_ct = Fin
    Fin_k  = Fin[params['CRYPTO_CIPHERTEXTBYTES']:] # Contains secret data
    shake_input_seedSE = empty(1 + params['CRYPTO_BYTES'], dtype=uint8) # Contains secret data

    # pkh <- G_1(pk), generate random mu, compute (seedSE || k) = G_2(pkh || mu)
    shake(pkh, params['BYTES_PKHASH'], pk, params['CRYPTO_PUBLICKEYBYTES'])
    # Array must have same dimens, it does not send refs, only copy vals
    # copyto(mu,array([randbyte for randbyte in secrets.token_bytes(params['BYTES_MU'])], dtype=uint8))
    copyto(mu, array([54, 97, 58, 117, 209, 149, 232, 204, 121, 171, 37, 137, 113, 241, 36, 188], dtype=uint8))
    shake(G2out, params['CRYPTO_BYTES']+params['CRYPTO_BYTES'], G2in, params['BYTES_PKHASH']+params['BYTES_MU'])

    # Generate Sp and Ep, and compute Bp = Sp*A + Ep. Generate A on-the-fly
    shake_input_seedSE[0] = 0x96
    shake_input_seedSE[1:] = seedSE[:params['CRYPTO_BYTES']]

    Sp.dtype = uint8
    sizeof_uint16 = 2
    shake(Sp, (2*params['PARAMS_N']+params['PARAMS_NBAR'])*params['PARAMS_NBAR']*sizeof_uint16,
          shake_input_seedSE, 1+params['CRYPTO_BYTES'])
    Sp.dtype = uint16

    Sp[(2*params['PARAMS_N']+params['PARAMS_N'])*params['PARAMS_NBAR']:] = \
        LE_TO_UINT16(Sp[(2*params['PARAMS_N']+params['PARAMS_N'])*params['PARAMS_NBAR']:])

    frodo_sample_n(Sp, params['PARAMS_N']*params['PARAMS_NBAR'], **params)
    frodo_sample_n(Ep, params['PARAMS_N']*params['PARAMS_NBAR'], **params)

    frodo_mul_add_sa_plus_e(Bp, Sp, Ep, pk_seedA, **params)
    frodo_pack(ct_c1,
               (params['PARAMS_LOGQ']*params['PARAMS_N']*params['PARAMS_NBAR'])//8,
               Bp, params['PARAMS_N']*params['PARAMS_NBAR'],
               params['PARAMS_LOGQ'])


    # Generate Epp, and compute V = Sp * B + Epp
    frodo_sample_n(Epp, params['PARAMS_NBAR']**2, **params)
    frodo_unpack(B, params['PARAMS_N']*params['PARAMS_NBAR'], pk_b,
                 params['CRYPTO_PUBLICKEYBYTES'] - params['BYTES_SEED_A'], params['PARAMS_LOGQ'])

    frodo_mul_add_sb_plus_e(V, B, Sp, Epp, **params)


    trc("B: ",len(V))
    trcl("B", V)


    exit()
#







def crypto_kem_dec(ct, ss, pk, shake, **params):
    print(params['PARAMS_N'])
#