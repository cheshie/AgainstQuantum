from sys import argv

from numpy import uint8, zeros, array, array_equal#, empty
from MISC import bigfile, trace
empty = zeros

trace.debug_mode = True
trcl = trace.tracelst
trc = trace.trace

# Test parameters
KEM_TEST_ITERATIONS = 100
KEM_BENCH_SECONDS   =  1

# Print message if more than one arg is specified
if len(argv) > 2:
    print("Program accepts only one argument.")
    print("Possible arguments: \n"
          "FrodoKEM-640 => default\n"
          "FrodoKEM-976\n"
          "FrodoKEM-1344\n")
    exit(1)
if len(argv) == 2:
    if argv[1] not in ["FrodoKEM-976","FrodoKEM-1344","FrodoKEM-640"]:
        print("Not allowed argument. Exiting")
        exit(1)

# according to passed arguments, import specific FrodoKEM system
# As each of three has different set of parameters
# Default option is FrodoKEM-640 - even if no args were supplied
if len(argv) == 1 or argv[1] == "FrodoKEM-640":
    from frodo640.api_frodo640 import crypto_kem_keypair_frodo640, crypto_kem_dec_frodo640 \
        , crypto_kem_enc_frodo640, FrodoKEM640Params, CRYPTO_ALGNAME as SYSTEM_NAME

    # Assign functions according to algorithm specified
    crypto_kem_keypair = crypto_kem_keypair_frodo640
    crypto_kem_enc     = crypto_kem_enc_frodo640
    crypto_kem_dec     = crypto_kem_dec_frodo640
# For future compatibility
# if argv[1] == "FrodoKEM-976":
#     from api_frodo976 import *
# if argv[1] == "FrodoKEM-1344":
#     from api_frodo1344 import *

#global params


def kem_test(named_parameters, iterations):
    # print("=============================================================================================================================\n");
    # print("Testing correctness of key encapsulation mechanism (KEM), system %s, tests for %d iterations\n" %
          # (named_parameters, iterations));
    # print("=============================================================================================================================\n");
    # Keypair => tested => OK!

    randomness = array(bigfile.randomness, dtype=uint8)

    # paramsTest = KEMValues()
    # crypto_kem_keypair(paramsTest.pk, paramsTest.sk)

    for x in range(200): #range(iterations):
        params = KEMValues()
        # params.pk = paramsTest.pk.copy()
        # params.sk = paramsTest.sk.copy()

        crypto_kem_keypair(params.pk, params.sk)
        crypto_kem_enc(params.ct, params.ss_encap, params.pk)
        # TODO: PK == PK, CT == CT, SK == SK SO WHAT IS WRONG??
        crypto_kem_dec(params.ss_decap, params.ct, params.sk)

        # trc("ct: ",len(params.ct))
        # trcl("ct",params.ct)
        # trc("pk: ", len(params.pk))
        # trcl("pk", params.pk)
        # trc("sk: ", len(params.sk))
        # trcl("sk", params.sk)
        # trcl("sk", params.sk)
        # trc("\n\n\n")

        # KEYS ARE OK (200 checks). Need to check encryption now


        # crypto_kem_enc(params.ct, params.ss_encap, params.pk)
        # crypto_kem_dec(params.ss_decap, params.ct, params.sk)

        # trc("ss", params.ss_encap == params.ss_decap)
        # trcl("ss_encap", params.ss_encap)
        # trcl("ss_encap", params.ss_decap)
        # trc("-" * 30)

        # crypto_kem_dec(params.ss_decap, params.ct, params.sk)
        # trcl("ss_encap: ",params.ss_encap)
        # trcl("ss_decap: ", params.ss_decap)
        # trc("\n\n")

        if array_equal(params.ss_encap,params.ss_decap) is not True:
            print("ERROR!")
            # return False
        else:
            print("Keys equal.")

    # print("Tests PASSED. All sessions keys matched.\n")
    return True
#


# def kem_bench(seconds):
    # What are iterations in the original???
    # print("Key generation: ",timeit(lambda: crypto_kem_keypair(params.pk, params.sk),'gc.enable()',number=KEM_TEST_ITERATIONS))
    # print("KEM encapsulation: ", timeit(lambda: crypto_kem_enc(params.ct, params.ss_encap, params.pk),'gc.enable()',number=KEM_TEST_ITERATIONS)) #'crypto_kem_enc(ct, ss_encap, pk)', globals=globals()
    # print("KEM decapsulation: ", timeit(lambda: crypto_kem_dec(params.ss_decap, params.ct, params.sk),'gc.enable()',number=KEM_TEST_ITERATIONS)) #'crypto_kem_dec(ss_decap, ct, sk)', globals=globals()
#


def main():
    OK = True
    OK = kem_test(SYSTEM_NAME, KEM_TEST_ITERATIONS)

    # if OK is True:
    #     kem_bench(KEM_BENCH_SECONDS)

    exit(0)


# main function execution
main()