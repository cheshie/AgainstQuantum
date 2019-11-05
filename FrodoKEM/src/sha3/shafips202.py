from numpy import uint8, array, zeros, uint64, ulonglong, copyto

from MISC import trace

trace.debug_mode = True
trcl = trace.tracelst
trc = trace.trace

global SHAKE128_RATE
global SHAKE256_RATE
global NROUNDS
global KeccakF_RoundConstants

SHAKE128_RATE = 168
SHAKE256_RATE = 136
NROUNDS = 24

KeccakF_RoundConstants = array(
    [
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808a,
    0x8000000080008000,
    0x000000000000808b,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008a,
    0x0000000000000088,
    0x0000000080008009,
    0x000000008000000a,
    0x000000008000808b,
    0x800000000000008b,
    0x8000000000008089,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800a,
    0x800000008000000a,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008
    ],
    dtype=uint64
)


def shake128(self, output, outlen, input_a, inlen):
    output_ref = output

    s = zeros(25, dtype=uint64)
    t = zeros(SHAKE128_RATE, dtype=uint8)
    nblocks = outlen // SHAKE128_RATE

    # Absorb input_a
    keccak_absorb(s, SHAKE128_RATE, input_a, inlen, 0x1F)

    # Squeeze output
    keccak_squeezeblocks(output, nblocks, s, SHAKE128_RATE)

    output_ref = output_ref[nblocks*SHAKE128_RATE:]

    outlen -= nblocks*SHAKE128_RATE

    if outlen:
        keccak_squeezeblocks(t, 1, s, SHAKE128_RATE)
        for i in range(outlen):
            output_ref[i] = t[i]
#


def keccak_absorb(s, r, m, mlen, p):
    t = zeros(200, dtype=uint8)

    while mlen >= r:
        for i in range(r//8):
            s[i] ^= load64(m[8 * i:])
        keccakf1600_state_permute(s)
        mlen -= r
        m = m[r:]

    t[:r] = 0
    t[:mlen] = m[:mlen]

    t[mlen] = p
    t[r - 1] |= uint64(128)

    for i in range(r//8):
        s[i] ^= load64(t[8 * i:])
#


def keccak_squeezeblocks(h, nblocks, s, r):
    while nblocks > 0:
        keccakf1600_state_permute(s)
        for i in range(r>>3):
            store64(h[8*i:], s[i])

        h = h[r:]
        nblocks -= 1
#


def load64(x):
    r = ulonglong(0)

    for i in range(8):
        i = ulonglong(i)
        r |= ulonglong(x[i]) << ulonglong(8) * i

    return r
#


def store64(x, u):
    for i in range(8):
        x[i] = uint8(u)
        u >>= uint64(8)
#


def keccakf1600_state_permute(state):
    ROL = lambda a,offset: (a << uint64(offset)) ^ (a >> uint64(64-offset))

    # CopyFromState(A, state)
    Aba,Abe,Abi,Abo,Abu,Aga,Age,Agi,Ago,Agu,Aka,Ake,Aki,\
    Ako,Aku,Ama,Ame,Ami,Amo,Amu,Asa,Ase,Asi,Aso,Asu = state

    for round in range(0,NROUNDS, 2):
        # prepareTheta
        BCa = Aba^Aga^Aka^Ama^Asa
        BCe = Abe^Age^Ake^Ame^Ase
        BCi = Abi^Agi^Aki^Ami^Asi
        BCo = Abo^Ago^Ako^Amo^Aso
        BCu = Abu^Agu^Aku^Amu^Asu

        # thetaRhoPiChiIotaPrepareTheta(round  , A, E)
        Da = BCu^ROL(BCe, 1)
        De = BCa^ROL(BCi, 1)
        Di = BCe^ROL(BCo, 1)
        Do = BCi^ROL(BCu, 1)
        Du = BCo^ROL(BCa, 1)
        
        Aba ^= Da
        BCa = Aba
        Age ^= De
        BCe = ROL(Age, 44)
        Aki ^= Di
        BCi = ROL(Aki, 43)
        Amo ^= Do
        BCo = ROL(Amo, 21)
        Asu ^= Du
        BCu = ROL(Asu, 14)
        Eba =   BCa ^((~BCe)&  BCi )
        Eba ^= KeccakF_RoundConstants[round] # it was casted to uint64 - should I worry?
        Ebe =   BCe ^((~BCi)&  BCo )
        Ebi =   BCi ^((~BCo)&  BCu )
        Ebo =   BCo ^((~BCu)&  BCa )
        Ebu =   BCu ^((~BCa)&  BCe )

        Abo ^= Do
        BCa = ROL(Abo, 28)
        Agu ^= Du
        BCe = ROL(Agu, 20)
        Aka ^= Da
        BCi = ROL(Aka,  3)
        Ame ^= De
        BCo = ROL(Ame, 45)
        Asi ^= Di
        BCu = ROL(Asi, 61)
        Ega =   BCa ^((~BCe)&  BCi )
        Ege =   BCe ^((~BCi)&  BCo )
        Egi =   BCi ^((~BCo)&  BCu )
        Ego =   BCo ^((~BCu)&  BCa )
        Egu =   BCu ^((~BCa)&  BCe )

        Abe ^= De
        BCa = ROL(Abe,  1)
        Agi ^= Di
        BCe = ROL(Agi,  6)
        Ako ^= Do
        BCi = ROL(Ako, 25)
        Amu ^= Du
        BCo = ROL(Amu,  8)
        Asa ^= Da
        BCu = ROL(Asa, 18)
        Eka =   BCa ^((~BCe)&  BCi )
        Eke =   BCe ^((~BCi)&  BCo )
        Eki =   BCi ^((~BCo)&  BCu )
        Eko =   BCo ^((~BCu)&  BCa )
        Eku =   BCu ^((~BCa)&  BCe )
        
        Abu ^= Du
        BCa = ROL(Abu, 27)
        Aga ^= Da
        BCe = ROL(Aga, 36)
        Ake ^= De
        BCi = ROL(Ake, 10)
        Ami ^= Di
        BCo = ROL(Ami, 15)
        Aso ^= Do
        BCu = ROL(Aso, 56)
        Ema =   BCa ^((~BCe)&  BCi )
        Eme =   BCe ^((~BCi)&  BCo )
        Emi =   BCi ^((~BCo)&  BCu )
        Emo =   BCo ^((~BCu)&  BCa )
        Emu =   BCu ^((~BCa)&  BCe )
        
        Abi ^= Di
        BCa = ROL(Abi, 62)
        Ago ^= Do
        BCe = ROL(Ago, 55)
        Aku ^= Du
        BCi = ROL(Aku, 39)
        Ama ^= Da
        BCo = ROL(Ama, 41)
        Ase ^= De
        BCu = ROL(Ase,  2)
        Esa =   BCa ^((~BCe)&  BCi )
        Ese =   BCe ^((~BCi)&  BCo )
        Esi =   BCi ^((~BCo)&  BCu )
        Eso =   BCo ^((~BCu)&  BCa )
        Esu =   BCu ^((~BCa)&  BCe )

        # prepareTheta
        BCa = Eba^Ega^Eka^Ema^Esa
        BCe = Ebe^Ege^Eke^Eme^Ese
        BCi = Ebi^Egi^Eki^Emi^Esi
        BCo = Ebo^Ego^Eko^Emo^Eso
        BCu = Ebu^Egu^Eku^Emu^Esu
        
        # thetaRhoPiChiIotaPrepareTheta(round+1, E, A)
        Da = BCu^ROL(BCe, 1)
        De = BCa^ROL(BCi, 1)
        Di = BCe^ROL(BCo, 1)
        Do = BCi^ROL(BCu, 1)
        Du = BCo^ROL(BCa, 1)
        
        Eba ^= Da
        BCa = Eba
        Ege ^= De
        BCe = ROL(Ege, 44)
        Eki ^= Di
        BCi = ROL(Eki, 43)
        Emo ^= Do
        BCo = ROL(Emo, 21)
        Esu ^= Du
        BCu = ROL(Esu, 14)
        Aba =   BCa ^((~BCe)&  BCi )
        Aba ^= KeccakF_RoundConstants[round+1] # it was casted to uint64 - should I worry?
        Abe =   BCe ^((~BCi)&  BCo )
        Abi =   BCi ^((~BCo)&  BCu )
        Abo =   BCo ^((~BCu)&  BCa )
        Abu =   BCu ^((~BCa)&  BCe )
        
        Ebo ^= Do
        BCa = ROL(Ebo, 28)
        Egu ^= Du
        BCe = ROL(Egu, 20)
        Eka ^= Da
        BCi = ROL(Eka, 3)
        Eme ^= De
        BCo = ROL(Eme, 45)
        Esi ^= Di
        BCu = ROL(Esi, 61)
        Aga =   BCa ^((~BCe)&  BCi )
        Age =   BCe ^((~BCi)&  BCo )
        Agi =   BCi ^((~BCo)&  BCu )
        Ago =   BCo ^((~BCu)&  BCa )
        Agu =   BCu ^((~BCa)&  BCe )

        Ebe ^= De
        BCa = ROL(Ebe, 1)
        Egi ^= Di
        BCe = ROL(Egi, 6)
        Eko ^= Do
        BCi = ROL(Eko, 25)
        Emu ^= Du
        BCo = ROL(Emu, 8)
        Esa ^= Da
        BCu = ROL(Esa, 18)
        Aka =   BCa ^((~BCe)&  BCi )
        Ake =   BCe ^((~BCi)&  BCo )
        Aki =   BCi ^((~BCo)&  BCu )
        Ako =   BCo ^((~BCu)&  BCa )
        Aku =   BCu ^((~BCa)&  BCe )
        
        Ebu ^= Du
        BCa = ROL(Ebu, 27)
        Ega ^= Da
        BCe = ROL(Ega, 36)
        Eke ^= De
        BCi = ROL(Eke, 10)
        Emi ^= Di
        BCo = ROL(Emi, 15)
        Eso ^= Do
        BCu = ROL(Eso, 56)
        Ama =   BCa ^((~BCe)&  BCi )
        Ame =   BCe ^((~BCi)&  BCo )
        Ami =   BCi ^((~BCo)&  BCu )
        Amo =   BCo ^((~BCu)&  BCa )
        Amu =   BCu ^((~BCa)&  BCe )
        
        Ebi ^= Di
        BCa = ROL(Ebi, 62)
        Ego ^= Do
        BCe = ROL(Ego, 55)
        Eku ^= Du
        BCi = ROL(Eku, 39)
        Ema ^= Da
        BCo = ROL(Ema, 41)
        Ese ^= De
        BCu = ROL(Ese, 2)
        Asa =   BCa ^((~BCe)&  BCi )
        Ase =   BCe ^((~BCi)&  BCo )
        Asi =   BCi ^((~BCo)&  BCu )
        Aso =   BCo ^((~BCu)&  BCa )
        Asu =   BCu ^((~BCa)&  BCe )

    # Copy_to_state(state, A)
    copyto(state, array([Aba,Abe,Abi,Abo,Abu,Aga,Age,Agi,Ago,Agu,Aka,Ake,Aki,Ako,Aku,Ama,\
    Ame,Ami,Amo,Amu,Asa,Ase,Asi,Aso,Asu]))
#