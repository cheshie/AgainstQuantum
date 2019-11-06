from sys import argv
from timeit import Timer
from numpy import array_equal
from statistics import mean, stdev
from MISC import trace

trace.debug_mode = True
trcl = trace.tracelst
trc = trace.trace

# Test parameters
KEM_TEST_ITERATIONS = 2
KEM_BENCH_SECONDS   = 1
REPETITIONS         = 2

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
    from frodo640.api_frodo640 import FrodoAPI640
    # Assign functions according to algorithm specified
    FrodoAPI640 = FrodoAPI640()
    crypto_kem_keypair = FrodoAPI640.crypto_kem_keypair_frodo640
    crypto_kem_enc     = FrodoAPI640.crypto_kem_enc_frodo640
    crypto_kem_dec     = FrodoAPI640.crypto_kem_dec_frodo640
# For future compatibility
# if argv[1] == "FrodoKEM-976":
#     from api_frodo976 import *
# if argv[1] == "FrodoKEM-1344":
#     from api_frodo1344 import *


def kem_test(named_parameters, iterations):
    print("=" * 125, "\n");
    print(f"Testing correctness of key encapsulation mechanism (KEM), system {named_parameters},"
          f" tests for {iterations} iterations\n")
    print("=" * 125, "\n");

    for x in range(iterations):
        crypto_kem_keypair()
        ss_encap = crypto_kem_enc()
        ss_decap = crypto_kem_dec()

        if array_equal(ss_encap, ss_decap) is not True:
            print("ERROR!")
            return False
        else:
            print("Keys equal.")

    print("Tests PASSED. All sessions keys matched.\n")
    return True
#


def kem_bench(seconds):
    print(20 * " ", "{:<10s} {:<10s} {:<10s} {:<10s}".format("Total", "Average", "Best", "Std.dev"))
    temp = Timer(lambda: crypto_kem_keypair(),'gc.enable()').repeat(repeat=KEM_TEST_ITERATIONS, number=REPETITIONS)
    print("   Key generation: {:2.3f} {} {}".format(sum(temp),mean(temp),min(temp),stdev(temp)))
    temp = Timer(lambda: crypto_kem_enc(),'gc.enable()').repeat(repeat=KEM_TEST_ITERATIONS, number=REPETITIONS)
    print("KEM encapsulation: {} {} {}".format(sum(temp),mean(temp),min(temp),stdev(temp)))
    temp = Timer(lambda: crypto_kem_dec(),'gc.enable()').repeat(repeat=KEM_TEST_ITERATIONS, number=REPETITIONS)
    print("KEM decapsulation: {} {} {}".format(sum(temp),mean(temp),min(temp),stdev(temp)))
#


def main():
    OK = True
    # OK = kem_test(FrodoAPI640.CRYPTO_ALGNAME, KEM_TEST_ITERATIONS)

    if OK is True:
        kem_bench(KEM_BENCH_SECONDS)

    exit(0)


# main function execution
main()