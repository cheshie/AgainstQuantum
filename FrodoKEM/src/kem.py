from numpy import array, zeros, uint8, uint16, frombuffer, copyto, empty
import secrets
from FrodoKEM.src.config import LE_TO_UINT16, UINT16_TO_LE
from FrodoKEM.src.frodo_macrify import Frodo
from FrodoKEM.src.noise import frodo_sample_n
from FrodoKEM.src.util import frodo_pack, frodo_unpack
# empty = zeros


class CryptoKem(Frodo):
    @staticmethod
    def keypair(pm: 'Referencing params of specific FrodoKEM version', pk: 'public key',
                sk: 'secret key') -> (array, array):
        # Generate the secret values, the seed for S and E, and
        #the seed for the seed for A.Add seed_A to the public key
        pk_seedA = pk
        pk_b     = pk[pm.BYTES_SEED_A:]
        sk_s     = sk
        sk_pk    = sk[pm.CRYPTO_BYTES:]
        sk_S     = sk[pm.CRYPTO_BYTES+pm.CRYPTO_PUBLICKEYBYTES:]
        sk_pkh   = sk[pm.CRYPTO_BYTES+pm.CRYPTO_PUBLICKEYBYTES+2*pm.PARAMS_N*pm.PARAMS_NBAR:]
        B = zeros(pm.PARAMS_N*pm.PARAMS_NBAR, dtype=uint16)
        S = zeros(2*pm.PARAMS_N*pm.PARAMS_NBAR, dtype=uint16)
        E = S[pm.PARAMS_N*pm.PARAMS_NBAR:]

        rcount = 2 * pm.CRYPTO_BYTES + pm.BYTES_SEED_A
        randomness =  array([randbyte for randbyte in secrets.token_bytes(rcount)], dtype=uint8)
        randomness_s = randomness
        randomness_seedSE = randomness[pm.CRYPTO_BYTES:]
        randomness_z = randomness[2*pm.CRYPTO_BYTES:]
        shake_input_seedSE = zeros(1 + pm.CRYPTO_BYTES, dtype=uint8)
        pm.shake(pk_seedA, pm.BYTES_SEED_A, randomness_z, pm.BYTES_SEED_A)

        # Generate S and E, compute B = A*S + E. Generate A on-the-fly
        shake_input_seedSE[0] = 0x5F
        shake_input_seedSE[1:pm.CRYPTO_BYTES+1] = randomness_seedSE[:pm.CRYPTO_BYTES]
        S.dtype=uint8; sizeof_uint16 = 2

        pm.shake(S, 2*pm.PARAMS_N*pm.PARAMS_NBAR*sizeof_uint16,
              shake_input_seedSE, 1 + pm.CRYPTO_BYTES); S.dtype=uint16

        S = UINT16_TO_LE(S)

        frodo_sample_n(S, pm.PARAMS_N*pm.PARAMS_NBAR, pm)
        frodo_sample_n(E, pm.PARAMS_N*pm.PARAMS_NBAR, pm)
        Frodo.mul_add_as_plus_e(pm, B, S, E, pk)

        # Encode the second part of the public key
        frodo_pack(pk_b, pm.CRYPTO_PUBLICKEYBYTES - pm.BYTES_SEED_A,
                   B, pm.PARAMS_N*pm.PARAMS_NBAR, pm.PARAMS_LOGQ)

        # Add s, pk and S to the secret key
        sk_s[:pm.CRYPTO_BYTES] = randomness_s[:pm.CRYPTO_BYTES]
        # This is safe - sk_pk does get copy of range of els in pk
        sk_pk[:pm.CRYPTO_PUBLICKEYBYTES] = pk[:pm.CRYPTO_PUBLICKEYBYTES]

        #Convert uint16 to little endian
        S[:pm.PARAMS_N*pm.PARAMS_NBAR] =\
            UINT16_TO_LE(S[:pm.PARAMS_N*pm.PARAMS_NBAR])

        sk_S[:2 * pm.PARAMS_N*pm.PARAMS_NBAR] =\
            frombuffer(S[:pm.PARAMS_N*pm.PARAMS_NBAR].tobytes(),dtype=uint8).copy()

        # Add H(pk) to the secret key
        pm.shake(sk_pkh, pm.BYTES_PKHASH, pk, pm.CRYPTO_PUBLICKEYBYTES)

        # Cleanup
        S[:pm.PARAMS_N*pm.PARAMS_NBAR] = 0
        E[:pm.PARAMS_N*pm.PARAMS_NBAR] = 0
        randomness[:2*pm.CRYPTO_BYTES] = 0
        shake_input_seedSE[:1 + pm.CRYPTO_BYTES] = 0

        return pk, sk
    #

    @staticmethod
    def enc(pm: 'Referencing params of specific FrodoKEM version', ct: 'ciphertext', ss: 'shared secret',
            pk: 'public key') -> array:
        # FrodoKEM's key encapsulation
        pk_seedA = pk
        pk_b     = pk[pm.BYTES_SEED_A:]
        ct_c1    = ct
        ct_c2    = ct[(pm.PARAMS_LOGQ * pm.PARAMS_N * pm.PARAMS_NBAR)//8:]
        B = zeros(pm.PARAMS_N * pm.PARAMS_NBAR, dtype=uint16)
        V = zeros(pm.PARAMS_NBAR ** 2, dtype=uint16) # Contains secret data
        C = zeros(pm.PARAMS_NBAR ** 2, dtype=uint16)

        Bp = zeros(pm.PARAMS_N * pm.PARAMS_NBAR, dtype=uint16)
        Sp = zeros((2 * pm.PARAMS_N + pm.PARAMS_NBAR) * pm.PARAMS_NBAR, dtype=uint16) # contains secret data
        Ep = Sp[pm.PARAMS_N * pm.PARAMS_NBAR:] # Contains secret data
        Epp= Sp[2 * pm.PARAMS_N * pm.PARAMS_NBAR:] # Contains secret data

        G2in = empty(pm.BYTES_PKHASH+pm.BYTES_MU, dtype=uint8) # Contains secret data via mu
        pkh  = G2in
        mu   = G2in[pm.BYTES_PKHASH:] # Contains secret data
        G2out= empty(2 * pm.CRYPTO_BYTES, dtype=uint8) # Contains secret data
        seedSE = G2out # Contains secret data
        k = G2out[pm.CRYPTO_BYTES:] # Contains secret data
        Fin    = empty(pm.CRYPTO_CIPHERTEXTBYTES + pm.CRYPTO_BYTES, dtype=uint8) # Contains secret data via Fin_k
        Fin_ct = Fin
        Fin_k  = Fin[pm.CRYPTO_CIPHERTEXTBYTES:] # Contains secret data
        shake_input_seedSE = empty(1 + pm.CRYPTO_BYTES, dtype=uint8) # Contains secret data

        # pkh <- G_1(pk), generate random mu, compute (seedSE || k) = G_2(pkh || mu)
        pm.shake(pkh, pm.BYTES_PKHASH, pk, pm.CRYPTO_PUBLICKEYBYTES)
        copyto(mu,array([randbyte for randbyte in secrets.token_bytes(pm.BYTES_MU)], dtype=uint8))
        pm.shake(G2out, pm.CRYPTO_BYTES+pm.CRYPTO_BYTES, G2in, pm.BYTES_PKHASH+pm.BYTES_MU)

        # Generate Sp and Ep, and compute Bp = Sp*A + Ep. Generate A on-the-fly
        shake_input_seedSE[0] = 0x96
        shake_input_seedSE[1:] = seedSE[:pm.CRYPTO_BYTES]

        Sp.dtype = uint8
        sizeof_uint16 = 2
        pm.shake(Sp, (2*pm.PARAMS_N+pm.PARAMS_NBAR)*pm.PARAMS_NBAR*sizeof_uint16,
              shake_input_seedSE, 1+pm.CRYPTO_BYTES)
        Sp.dtype = uint16

        Sp[(2*pm.PARAMS_N+pm.PARAMS_N)*pm.PARAMS_NBAR:] = \
            LE_TO_UINT16(Sp[(2*pm.PARAMS_N+pm.PARAMS_N)*pm.PARAMS_NBAR:])

        frodo_sample_n(Sp, pm.PARAMS_N*pm.PARAMS_NBAR, pm)
        frodo_sample_n(Ep, pm.PARAMS_N*pm.PARAMS_NBAR, pm)

        Frodo.mul_add_sa_plus_e(pm, Bp, Sp, Ep, pk_seedA)
        frodo_pack(ct_c1, (pm.PARAMS_LOGQ*pm.PARAMS_N*pm.PARAMS_NBAR)//8,
                   Bp, pm.PARAMS_N*pm.PARAMS_NBAR, pm.PARAMS_LOGQ)

        # Generate Epp, and compute V = Sp * B + Epp
        frodo_sample_n(Epp, pm.PARAMS_NBAR**2, pm)
        frodo_unpack(B, pm.PARAMS_N*pm.PARAMS_NBAR, pk_b,
                     pm.CRYPTO_PUBLICKEYBYTES - pm.BYTES_SEED_A, pm.PARAMS_LOGQ)

        Frodo.mul_add_sb_plus_e(pm, V, B, Sp, Epp)

        # Encode mu, and compute C = V + enc(mu)(mod q)
        mu.dtype = uint16
        Frodo.key_encode(pm, C, mu) ;mu.dtype = uint8
        Frodo.add(pm, C, V, C)
        frodo_pack(ct_c2, (pm.PARAMS_LOGQ*pm.PARAMS_NBAR**2)//8, C,
                   pm.PARAMS_NBAR**2, pm.PARAMS_LOGQ)

        # Compute ss = F(ct||KK)
        Fin_ct[:pm.CRYPTO_CIPHERTEXTBYTES] = ct[:pm.CRYPTO_CIPHERTEXTBYTES]
        Fin_k[:pm.CRYPTO_BYTES] = k[:pm.CRYPTO_BYTES]
        pm.shake(ss, pm.CRYPTO_BYTES, Fin, pm.CRYPTO_CIPHERTEXTBYTES + pm.CRYPTO_BYTES)

        # Cleanup
        V[:pm.PARAMS_NBAR*pm.PARAMS_NBAR] = 0
        Sp[:pm.PARAMS_N * pm.PARAMS_NBAR] = 0
        Ep[:pm.PARAMS_N * pm.PARAMS_NBAR] = 0
        Epp[:pm.PARAMS_NBAR * pm.PARAMS_NBAR] = 0
        mu[:pm.BYTES_MU] = 0
        G2out[:2 * pm.CRYPTO_BYTES] = 0
        Fin_k[:pm.CRYPTO_BYTES] = 0
        shake_input_seedSE[:1 + pm.CRYPTO_BYTES] = 0

        return ct, ss
    #

    @staticmethod
    def dec(pm: 'Referencing params of specific FrodoKEM version', ss: 'shared secret', ct: 'ciphertext',
            sk: 'private key') -> array:
        # FrodoKEM's key decapsulation
        B  = zeros(pm.PARAMS_N * pm.PARAMS_NBAR, dtype=uint16)
        Bp = zeros(pm.PARAMS_N * pm.PARAMS_NBAR, dtype=uint16)
        W  = zeros(pm.PARAMS_NBAR ** 2, dtype=uint16)  # Contains secret data
        C  = zeros(pm.PARAMS_NBAR ** 2, dtype=uint16)
        CC = zeros(pm.PARAMS_NBAR ** 2, dtype=uint16)

        BBp = zeros(pm.PARAMS_N * pm.PARAMS_NBAR, dtype=uint16)
        Sp  = zeros((2 * pm.PARAMS_N + pm.PARAMS_NBAR) * pm.PARAMS_NBAR, dtype=uint16)
        Ep  = Sp[pm.PARAMS_N * pm.PARAMS_NBAR:]  # Contains secret data
        Epp = Sp[2 * pm.PARAMS_N * pm.PARAMS_NBAR:]  # Contains secret data

        ct_c1 = ct
        ct_c2 = ct[(pm.PARAMS_LOGQ * pm.PARAMS_N * pm.PARAMS_NBAR) // 8:]
        sk_s  = sk
        sk_pk = sk[pm.CRYPTO_BYTES:]
        sk_S  = sk[pm.CRYPTO_BYTES + pm.CRYPTO_PUBLICKEYBYTES:] ; sk_S.dtype = uint16
        S = empty(pm.PARAMS_N * pm.PARAMS_NBAR, dtype=uint16)
        sk_pkh = sk[pm.CRYPTO_BYTES + pm.CRYPTO_PUBLICKEYBYTES + 2 * pm.PARAMS_N * pm.PARAMS_NBAR:]
        pk_seedA = sk_pk
        pk_b = sk_pk[pm.BYTES_SEED_A:]

        G2in = empty(pm.BYTES_PKHASH + pm.BYTES_MU, dtype=uint8) # contains secret data via muprime
        pkh  = G2in
        muprime = G2in[pm.BYTES_PKHASH:] # contains secret data
        G2out   = empty(2 * pm.CRYPTO_BYTES, dtype=uint8) # contains secret data
        seedSEprime = G2out # contains secret data
        kprime = G2out[pm.CRYPTO_BYTES:] # contains secret data
        Fin    = empty(pm.CRYPTO_CIPHERTEXTBYTES + pm.CRYPTO_BYTES, dtype=uint8) # contains secret data via Fin_k
        Fin_ct = Fin
        Fin_k  = Fin[pm.CRYPTO_CIPHERTEXTBYTES:] # contains secret data
        shake_input_seedSEprime = empty(1 + pm.CRYPTO_BYTES, dtype=uint8) # contains secret data

        S[:pm.PARAMS_N*pm.PARAMS_NBAR] = LE_TO_UINT16(sk_S[:pm.PARAMS_N*pm.PARAMS_NBAR])

        # Compute W = C - Bp * S(mod q), and decode the randomness mu
        frodo_unpack(Bp, pm.PARAMS_N*pm.PARAMS_NBAR,
            ct_c1, (pm.PARAMS_LOGQ*pm.PARAMS_N*pm.PARAMS_NBAR)//8, pm.PARAMS_LOGQ)
        frodo_unpack(C, pm.PARAMS_NBAR * pm.PARAMS_NBAR,
            ct_c2, (pm.PARAMS_LOGQ * pm.PARAMS_NBAR ** 2) // 8, pm.PARAMS_LOGQ)
        Frodo.mul_bs(pm, W, Bp, S)
        Frodo.sub(pm, W, C, W)
        muprime.dtype = uint16
        Frodo.key_decode(pm, muprime, W) ; muprime.dtype = uint8

        # Generate (seedSE' || k') = G_2(pkh || mu')
        pkh[:pm.BYTES_PKHASH] = sk_pkh[:pm.BYTES_PKHASH]
        pm.shake(G2out, 2 * pm.CRYPTO_BYTES, G2in, pm.BYTES_PKHASH + pm.BYTES_MU)

        # Generate Sp and Ep, and compute BBp = Sp * A + Ep. Generate A on-the-fly
        shake_input_seedSEprime[0] = 0x96
        shake_input_seedSEprime[1:pm.CRYPTO_BYTES + 1] = seedSEprime[:pm.CRYPTO_BYTES]
        Sp.dtype = uint8
        sizeof_uint16 = 2
        pm.shake(Sp, (2 * pm.PARAMS_N + pm.PARAMS_NBAR) * pm.PARAMS_NBAR * sizeof_uint16,
              shake_input_seedSEprime, 1 + pm.CRYPTO_BYTES) ; Sp.dtype = uint16
        Sp[:(2 * pm.PARAMS_N + pm.PARAMS_NBAR) * pm.PARAMS_NBAR] =\
            LE_TO_UINT16(Sp[:(2 * pm.PARAMS_N + pm.PARAMS_NBAR) * pm.PARAMS_NBAR])
        frodo_sample_n(Sp, pm.PARAMS_N * pm.PARAMS_NBAR, pm)
        frodo_sample_n(Ep, pm.PARAMS_N * pm.PARAMS_NBAR, pm)
        Frodo.mul_add_sa_plus_e(pm, BBp, Sp, Ep, pk_seedA)

        # Generate Epp and compute W = Sp*B + Epp
        frodo_sample_n(Ep, pm.PARAMS_NBAR ** 2, pm)
        frodo_unpack(B, pm.PARAMS_N*pm.PARAMS_NBAR,
                     pk_b, pm.CRYPTO_PUBLICKEYBYTES - pm.BYTES_SEED_A, pm.PARAMS_LOGQ)
        Frodo.mul_add_sb_plus_e(pm, W, B, Sp, Epp)

        # Encode mu and compute CC = W + enc(mu') (mod q)
        muprime.dtype = uint16
        Frodo.key_encode(pm, CC, muprime); muprime.dtype = uint8
        Frodo.add(pm, CC, W, CC)

        # Prepare input to F
        Fin_ct[:pm.CRYPTO_CIPHERTEXTBYTES] = ct[:pm.CRYPTO_CIPHERTEXTBYTES]

        # Reducing BBp modulo q
        BBp[:pm.PARAMS_N*pm.PARAMS_NBAR] =\
            BBp[:pm.PARAMS_N*pm.PARAMS_NBAR] & ((1 << pm.PARAMS_LOGQ) - 1)

        # Is (Bp == BBp & C == CC) == true
        if Bp[:2 * pm.PARAMS_N * pm.PARAMS_NBAR].all() == BBp[:2 * pm.PARAMS_N * pm.PARAMS_NBAR].all() and\
            C[:2 * pm.PARAMS_NBAR ** 2].all() == CC[:2 * pm.PARAMS_NBAR ** 2].all():
            # Load k' to do ss = F(ct || k')
            Fin_k[:pm.CRYPTO_BYTES] = kprime[:pm.CRYPTO_BYTES]
        else:
            # Load s to do ss = F(ct || s)
            Fin_k[:pm.CRYPTO_BYTES] = sk_s[:pm.CRYPTO_BYTES]

        pm.shake(ss, pm.CRYPTO_BYTES, Fin, pm.CRYPTO_CIPHERTEXTBYTES + pm.CRYPTO_BYTES)

        # Cleanup
        W[:pm.PARAMS_NBAR ** 2] = 0
        Sp[:pm.PARAMS_NBAR * pm.PARAMS_N] = 0
        S[:pm.PARAMS_NBAR * pm.PARAMS_N] = 0
        Ep[:pm.PARAMS_NBAR * pm.PARAMS_N] = 0
        Epp[:pm.PARAMS_NBAR ** 2] = 0
        muprime[:pm.BYTES_MU] = 0
        G2out[:2 * pm.CRYPTO_BYTES] = 0
        Fin_k[:pm.CRYPTO_BYTES] = 0
        shake_input_seedSEprime[:1 + pm.CRYPTO_BYTES] = 0

        return ss
    #
#