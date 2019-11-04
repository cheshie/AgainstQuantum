from numpy import array, zeros, uint8, uint16, frombuffer, copyto#, empty
import secrets
from MISC import trace
from src.config import LE_TO_UINT16, UINT16_TO_LE
from src.frodo_macrify import frodo_mul_add_as_plus_e, frodo_mul_add_sa_plus_e, \
    frodo_mul_add_sb_plus_e, frodo_key_encode, frodo_add, frodo_mul_bs, frodo_sub, frodo_key_decode
from src.noise import frodo_sample_n
from src.util import frodo_pack, frodo_unpack

empty = zeros

trace.debug_mode = True
trcl = trace.tracelst
trc = trace.trace


class CryptoKem():

    @classmethod
    def keypair(self, pk, sk):
        # Generate the secret values, the seed for S and E, and
        #the seed for the seed for A.Add seed_A to the public key
        pk_seedA = pk
        pk_b     = pk[self.BYTES_SEED_A:]
        sk_s     = sk
        sk_pk    = sk[self.CRYPTO_BYTES:]
        sk_S     = sk[self.CRYPTO_BYTES+self.CRYPTO_PUBLICKEYBYTES:]
        sk_pkh   = sk[self.CRYPTO_BYTES+self.CRYPTO_PUBLICKEYBYTES+2*self.PARAMS_N*self.PARAMS_NBAR:]
        B = zeros(self.PARAMS_N*self.PARAMS_NBAR,dtype=uint16)
        S = zeros(2*self.PARAMS_N*self.PARAMS_NBAR,dtype=uint16)
        E = S[self.PARAMS_N*self.PARAMS_NBAR:]

        rcount = 2 * self.CRYPTO_BYTES + self.BYTES_SEED_A
        randomness =  array([randbyte for randbyte in secrets.token_bytes(rcount)], dtype=uint8)
        # randomness = randomness1.copy()
        # trcl("randomness", randomness)
        # randomness = array([195, 42, 203, 181, 78, 183, 217, 4, 51, 106, 200, 157, 72, 124, 179, 143, 30, 209, 61, 196, 53,
        #                     59, 43, 115, 97, 172, 58, 185, 177, 163, 253, 110, 18, 55, 177, 14, 46, 108, 28, 107, 104, 211,
        #                     127, 74, 32, 175, 61, 154], dtype=uint8)
        randomness_s = randomness
        randomness_seedSE = randomness[self.CRYPTO_BYTES:]
        randomness_z = randomness[2*self.CRYPTO_BYTES:]
        shake_input_seedSE = zeros(1 + self.CRYPTO_BYTES,dtype=uint8)
        self.shake(pk_seedA, self.BYTES_SEED_A, randomness_z, self.BYTES_SEED_A)

        # Generate S and E, compute B = A*S + E. Generate A on-the-fly
        shake_input_seedSE[0] = 0x5F
        shake_input_seedSE[1:self.CRYPTO_BYTES+1] = randomness_seedSE[:self.CRYPTO_BYTES]
        S.dtype=uint8; sizeof_uint16 = 2

        self.shake(S,2*self.PARAMS_N*self.PARAMS_NBAR*sizeof_uint16,
              shake_input_seedSE, 1 + self.CRYPTO_BYTES); S.dtype=uint16

        S = UINT16_TO_LE(S)

        frodo_sample_n(S, self.PARAMS_N*self.PARAMS_NBAR)
        frodo_sample_n(E, self.PARAMS_N*self.PARAMS_NBAR)
        frodo_mul_add_as_plus_e(B, S, E, pk)

        # Encode the second part of the public key
        frodo_pack(pk_b, self.CRYPTO_PUBLICKEYBYTES - self.BYTES_SEED_A,
                   B, self.PARAMS_N*self.PARAMS_NBAR, self.PARAMS_LOGQ)

        # Add s, pk and S to the secret key
        sk_s[:self.CRYPTO_BYTES] = randomness_s[:self.CRYPTO_BYTES]
        # This is safe - sk_pk does get copy of range of els in pk
        sk_pk[:self.CRYPTO_PUBLICKEYBYTES] = pk[:self.CRYPTO_PUBLICKEYBYTES]

        #Convert uint16 to little endian
        S[:self.PARAMS_N*self.PARAMS_NBAR] =\
            UINT16_TO_LE(S[:self.PARAMS_N*self.PARAMS_NBAR])

        sk_S[:2 * self.PARAMS_N*self.PARAMS_NBAR] =\
            frombuffer(S[:self.PARAMS_N*self.PARAMS_NBAR].tobytes(),dtype=uint8).copy()

        # Add H(pk) to the secret key
        self.shake(sk_pkh, self.BYTES_PKHASH, pk, self.CRYPTO_PUBLICKEYBYTES)

        # Cleanup
        S[:self.PARAMS_N*self.PARAMS_NBAR] = 0
        E[:self.PARAMS_N*self.PARAMS_NBAR] = 0
        randomness[:2*self.CRYPTO_BYTES] = 0
        shake_input_seedSE[:1 + self.CRYPTO_BYTES] = 0

        return 0
    #

    @classmethod
    def enc(self, ct, ss, pk):
        # FrodoKEM's key encapsulation
        pk_seedA = pk
        pk_b     = pk[self.BYTES_SEED_A:]
        ct_c1    = ct
        ct_c2    = ct[(self.PARAMS_LOGQ * self.PARAMS_N * self.PARAMS_NBAR)//8:]
        B = zeros(self.PARAMS_N * self.PARAMS_NBAR, dtype=uint16)
        V = zeros(self.PARAMS_NBAR ** 2, dtype=uint16) # Contains secret data
        C = zeros(self.PARAMS_NBAR ** 2, dtype=uint16)

        Bp = zeros(self.PARAMS_N * self.PARAMS_NBAR, dtype=uint16)
        Sp = zeros((2 * self.PARAMS_N + self.PARAMS_NBAR) * self.PARAMS_NBAR, dtype=uint16) # contains secret data
        Ep = Sp[self.PARAMS_N * self.PARAMS_NBAR:] # Contains secret data
        Epp= Sp[2 * self.PARAMS_N * self.PARAMS_NBAR:] # Contains secret data

        G2in = empty(self.BYTES_PKHASH+self.BYTES_MU, dtype=uint8) # Contains secret data via mu
        pkh  = G2in
        mu   = G2in[self.BYTES_PKHASH:] # Contains secret data
        G2out= empty(2 * self.CRYPTO_BYTES, dtype=uint8) # Contains secret data
        seedSE = G2out # Contains secret data
        k = G2out[self.CRYPTO_BYTES:] # Contains secret data
        Fin    = empty(self.CRYPTO_CIPHERTEXTBYTES + self.CRYPTO_BYTES, dtype=uint8) # Contains secret data via Fin_k
        Fin_ct = Fin
        Fin_k  = Fin[self.CRYPTO_CIPHERTEXTBYTES:] # Contains secret data
        shake_input_seedSE = empty(1 + self.CRYPTO_BYTES, dtype=uint8) # Contains secret data

        # pkh <- G_1(pk), generate random mu, compute (seedSE || k) = G_2(pkh || mu)
        self.shake(pkh, self.BYTES_PKHASH, pk, self.CRYPTO_PUBLICKEYBYTES)
        copyto(mu,array([randbyte for randbyte in secrets.token_bytes(self.BYTES_MU)], dtype=uint8))
        # trcl("randomness", mu)
        # copyto(mu, array([51, 52, 165, 154, 205, 235, 13, 74, 157, 63, 137, 59, 155, 71, 221, 83], dtype=uint8))
        # copyto(mu, array([54, 97, 58, 117, 209, 149, 232, 204, 121, 171, 37, 137, 113, 241, 36, 188], dtype=uint8))
        self.shake(G2out, self.CRYPTO_BYTES+self.CRYPTO_BYTES, G2in, self.BYTES_PKHASH+self.BYTES_MU)

        # Generate Sp and Ep, and compute Bp = Sp*A + Ep. Generate A on-the-fly
        shake_input_seedSE[0] = 0x96
        shake_input_seedSE[1:] = seedSE[:self.CRYPTO_BYTES]

        Sp.dtype = uint8
        sizeof_uint16 = 2
        self.shake(Sp, (2*self.PARAMS_N+self.PARAMS_NBAR)*self.PARAMS_NBAR*sizeof_uint16,
              shake_input_seedSE, 1+self.CRYPTO_BYTES)
        Sp.dtype = uint16

        Sp[(2*self.PARAMS_N+self.PARAMS_N)*self.PARAMS_NBAR:] = \
            LE_TO_UINT16(Sp[(2*self.PARAMS_N+self.PARAMS_N)*self.PARAMS_NBAR:])

        frodo_sample_n(Sp, self.PARAMS_N*self.PARAMS_NBAR)
        frodo_sample_n(Ep, self.PARAMS_N*self.PARAMS_NBAR)

        frodo_mul_add_sa_plus_e(Bp, Sp, Ep, pk_seedA)
        frodo_pack(ct_c1,
                   (self.PARAMS_LOGQ*self.PARAMS_N*self.PARAMS_NBAR)//8,
                   Bp, self.PARAMS_N*self.PARAMS_NBAR,
                   self.PARAMS_LOGQ)


        # Generate Epp, and compute V = Sp * B + Epp
        frodo_sample_n(Epp, self.PARAMS_NBAR**2)
        frodo_unpack(B, self.PARAMS_N*self.PARAMS_NBAR, pk_b,
                     self.CRYPTO_PUBLICKEYBYTES - self.BYTES_SEED_A, self.PARAMS_LOGQ)

        frodo_mul_add_sb_plus_e(V, B, Sp, Epp)

        # Encode mu, and compute C = V + enc(mu)(mod q)
        mu.dtype = uint16
        frodo_key_encode(C, mu) ;mu.dtype = uint8
        frodo_add(C, V, C)
        frodo_pack(ct_c2, (self.PARAMS_LOGQ*self.PARAMS_NBAR**2)//8, C,
                   self.PARAMS_NBAR**2, self.PARAMS_LOGQ)

        # Compute ss = F(ct||KK)
        Fin_ct[:self.CRYPTO_CIPHERTEXTBYTES] = ct[:self.CRYPTO_CIPHERTEXTBYTES]
        Fin_k[:self.CRYPTO_BYTES] = k[:self.CRYPTO_BYTES]
        self.shake(ss, self.CRYPTO_BYTES, Fin, self.CRYPTO_CIPHERTEXTBYTES + self.CRYPTO_BYTES)

        # Cleanup
        V[:self.PARAMS_NBAR*self.PARAMS_NBAR] = 0
        Sp[:self.PARAMS_N * self.PARAMS_NBAR] = 0
        Ep[:self.PARAMS_N * self.PARAMS_NBAR] = 0
        Epp[:self.PARAMS_NBAR * self.PARAMS_NBAR] = 0
        mu[:self.BYTES_MU] = 0
        G2out[:2 * self.CRYPTO_BYTES] = 0
        Fin_k[:self.CRYPTO_BYTES] = 0
        shake_input_seedSE[:1 + self.CRYPTO_BYTES] = 0

        return 0
    #

    @classmethod
    def dec(self, ss, ct, sk):
        # FrodoKEM's key decapsulation
        B  = zeros(self.PARAMS_N * self.PARAMS_NBAR, dtype=uint16)
        Bp = zeros(self.PARAMS_N * self.PARAMS_NBAR, dtype=uint16)
        W  = zeros(self.PARAMS_NBAR ** 2, dtype=uint16)  # Contains secret data
        C  = zeros(self.PARAMS_NBAR ** 2, dtype=uint16)
        CC = zeros(self.PARAMS_NBAR ** 2, dtype=uint16)

        BBp = zeros(self.PARAMS_N * self.PARAMS_NBAR, dtype=uint16)
        Sp  = zeros((2 * self.PARAMS_N + self.PARAMS_NBAR) * self.PARAMS_NBAR, dtype=uint16)
        Ep  = Sp[self.PARAMS_N * self.PARAMS_NBAR:]  # Contains secret data
        Epp = Sp[2 * self.PARAMS_N * self.PARAMS_NBAR:]  # Contains secret data

        ct_c1 = ct
        ct_c2 = ct[(self.PARAMS_LOGQ * self.PARAMS_N * self.PARAMS_NBAR) // 8:]
        sk_s  = sk
        sk_pk = sk[self.CRYPTO_BYTES:]
        sk_S  = sk[self.CRYPTO_BYTES + self.CRYPTO_PUBLICKEYBYTES:] ; sk_S.dtype = uint16
        S = empty(self.PARAMS_N * self.PARAMS_NBAR, dtype=uint16)
        sk_pkh = sk[self.CRYPTO_BYTES + self.CRYPTO_PUBLICKEYBYTES + 2 * self.PARAMS_N * self.PARAMS_NBAR:]
        pk_seedA = sk_pk
        pk_b = sk_pk[self.BYTES_SEED_A:]

        G2in = empty(self.BYTES_PKHASH + self.BYTES_MU, dtype=uint8) # contains secret data via muprime
        pkh  = G2in
        muprime = G2in[self.BYTES_PKHASH:] # contains secret data
        G2out   = empty(2 * self.CRYPTO_BYTES, dtype=uint8) # contains secret data
        seedSEprime = G2out # contains secret data
        kprime = G2out[self.CRYPTO_BYTES:] # contains secret data
        Fin    = empty(self.CRYPTO_CIPHERTEXTBYTES + self.CRYPTO_BYTES, dtype=uint8) # contains secret data via Fin_k
        Fin_ct = Fin
        Fin_k  = Fin[self.CRYPTO_CIPHERTEXTBYTES:] # contains secret data
        shake_input_seedSEprime = empty(1 + self.CRYPTO_BYTES, dtype=uint8) # contains secret data

        S[:self.PARAMS_N*self.PARAMS_NBAR] = LE_TO_UINT16(sk_S[:self.PARAMS_N*self.PARAMS_NBAR])

        # Compute W = C - Bp * S(mod q), and decode the randomness mu
        frodo_unpack(Bp, self.PARAMS_N*self.PARAMS_NBAR,
            ct_c1, (self.PARAMS_LOGQ*self.PARAMS_N*self.PARAMS_NBAR)//8, self.PARAMS_LOGQ)
        frodo_unpack(C, self.PARAMS_NBAR * self.PARAMS_NBAR,
            ct_c2, (self.PARAMS_LOGQ * self.PARAMS_NBAR ** 2) // 8, self.PARAMS_LOGQ)
        frodo_mul_bs(W, Bp, S)
        frodo_sub(W, C, W)
        muprime.dtype = uint16
        frodo_key_decode(muprime, W) ; muprime.dtype = uint8

        # Generate (seedSE' || k') = G_2(pkh || mu')
        pkh[:self.BYTES_PKHASH] = sk_pkh[:self.BYTES_PKHASH]
        self.shake(G2out, 2 * self.CRYPTO_BYTES, G2in, self.BYTES_PKHASH + self.BYTES_MU)

        # Generate Sp and Ep, and compute BBp = Sp * A + Ep. Generate A on-the-fly
        shake_input_seedSEprime[0] = 0x96
        shake_input_seedSEprime[1:self.CRYPTO_BYTES + 1] = seedSEprime[:self.CRYPTO_BYTES]
        Sp.dtype = uint8
        sizeof_uint16 = 2
        self.shake(Sp, (2 * self.PARAMS_N + self.PARAMS_NBAR) * self.PARAMS_NBAR * sizeof_uint16,
              shake_input_seedSEprime, 1 + self.CRYPTO_BYTES) ; Sp.dtype = uint16
        Sp[:(2 * self.PARAMS_N + self.PARAMS_NBAR) * self.PARAMS_NBAR] =\
            LE_TO_UINT16(Sp[:(2 * self.PARAMS_N + self.PARAMS_NBAR) * self.PARAMS_NBAR])
        frodo_sample_n(Sp, self.PARAMS_N * self.PARAMS_NBAR)
        frodo_sample_n(Ep, self.PARAMS_N * self.PARAMS_NBAR)

        # TODO: Problem in this function = all params passing there are OK, BBp after function is not
        # TYPES OF PARAMS - OK
        frodo_mul_add_sa_plus_e(BBp, Sp, Ep, pk_seedA)

        # trc("tab: ", len(BBp))
        # trcl("tab", BBp)
        # exit()

        # Generate Epp and compute W = Sp*B + Epp
        frodo_sample_n(Ep, self.PARAMS_NBAR ** 2)
        frodo_unpack(B, self.PARAMS_N*self.PARAMS_NBAR,
                     pk_b, self.CRYPTO_PUBLICKEYBYTES - self.BYTES_SEED_A, self.PARAMS_LOGQ)
        frodo_mul_add_sb_plus_e(W, B, Sp, Epp)

        # Encode mu and compute CC = W + enc(mu') (mod q)
        muprime.dtype = uint16
        frodo_key_encode(CC, muprime); muprime.dtype = uint8
        frodo_add(CC, W, CC)

        # Prepare input to F
        Fin_ct[:self.CRYPTO_CIPHERTEXTBYTES] = ct[:self.CRYPTO_CIPHERTEXTBYTES]

        # Reducing BBp modulo q
        BBp[:self.PARAMS_N*self.PARAMS_NBAR] =\
            BBp[:self.PARAMS_N*self.PARAMS_NBAR] & ((1 << self.PARAMS_LOGQ) - 1)

        # TODO: Problem is: Bp is not equal to the BBp in this range => why?
        # Is (Bp == BBp & C == CC) == true
        if Bp[:2 * self.PARAMS_N * self.PARAMS_NBAR].all() == BBp[:2 * self.PARAMS_N * self.PARAMS_NBAR].all() and\
            C[:2 * self.PARAMS_NBAR ** 2].all() == CC[:2 * self.PARAMS_NBAR ** 2].all():
            # Load k' to do ss = F(ct || k')
            Fin_k[:self.CRYPTO_BYTES] = kprime[:self.CRYPTO_BYTES]
        else:
            # Load s to do ss = F(ct || s)
            Fin_k[:self.CRYPTO_BYTES] = sk_s[:self.CRYPTO_BYTES]

        self.shake(ss, self.CRYPTO_BYTES, Fin, self.CRYPTO_CIPHERTEXTBYTES + self.CRYPTO_BYTES)

        # Cleanup
        W[:self.PARAMS_NBAR ** 2] = 0
        Sp[:self.PARAMS_NBAR * self.PARAMS_N] = 0
        S[:self.PARAMS_NBAR * self.PARAMS_N] = 0
        Ep[:self.PARAMS_NBAR * self.PARAMS_N] = 0
        Epp[:self.PARAMS_NBAR ** 2] = 0
        muprime[:self.BYTES_MU] = 0
        G2out[:2 * self.CRYPTO_BYTES] = 0
        Fin_k[:self.CRYPTO_BYTES] = 0
        shake_input_seedSEprime[:1 + self.CRYPTO_BYTES]

        return 0
    #
#