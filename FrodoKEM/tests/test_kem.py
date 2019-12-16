from sys import argv
from timeit import Timer
from numpy import array_equal
from statistics import mean, stdev
from threading import Thread
import os
from time import sleep
from datetime import datetime
from enum import Enum

"""
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
"""
from FrodoKEM.frodo640.api_frodo640 import FrodoAPI640
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


def kem_test(named_parameters, iterations=2):
    class Operations(Enum):
        keyGeneration = 0
        keyEncapsulation = 1
        keyDecapsulation = 2

    def tester(iterations):
        global correct; correct = 0
        global incorrect; incorrect = 0
        global iteration_time; iteration_time = 0
        global current_operation; current_operation = 0
        # Add also percentage of incorrect results, or all results??

        # ADD VECTOR WITH INCORRECT RESULTS!!!
        start_time = datetime.now()
        for x in range(iterations):
            crypto_kem_keypair()
            current_operation += 1
            ss_encap = crypto_kem_enc()
            current_operation += 1
            ss_decap = crypto_kem_dec()
            current_operation += 1
            current_operation = current_operation % 3
            if array_equal(ss_encap, ss_decap) is not True:
                incorrect += 1
            else:
                correct   += 1
            iteration_time = (datetime.now() - start_time).total_seconds()
            start_time     = datetime.now()
        sleep(1)
    #

    test_thread = Thread(target=tester, args=(iterations,))
    test_thread.start()
    time_started = datetime.now()
    time_finished = 0
    while test_thread.isAlive():
        _ = os.system("clear")

        print("=" * 101, "\n")
        print(f"Testing correctness of key encapsulation mechanism (KEM), system {named_parameters},"
              f" tests for {iterations} iterations\n")
        print("=" * 101, "\n")
        print(f"Time started: {time_started}\n", end="")
        if iteration_time > 0:
            print(f"Estimated time: {int(iteration_time * (iterations - incorrect - correct))} seconds\n", end="")
        print(f"Current operation: {str(Operations(current_operation))[len('Operations.'):]}\n", end="")
        print(f"Current iteration: {incorrect+correct}\n", end="")
        print(f"Correct results: {correct}\n", end="")
        print(f"Incorrect results: {incorrect}\n", end="")
        progress = (incorrect + correct) * 20 // iterations
        print("["+"#" * progress + (20 - progress) * ' '+']',"("+str(progress / 20 * 100)+"%)") # <= change formula here??? It should not consider length of bar, only real results # MAKE IT INT
        sleep(1)

    # Thread synchronization
    test_thread.join()
    time_finished = datetime.now()

    print("Tests finished.\n")
    print("Time finished: ",time_finished)
    print("Tests have taken ", round((time_finished - time_started).total_seconds(), 2), "seconds")
    return True
#


# should not it be iterations 1? and repetitions 10 for ex, then it will execute that outer
# loop 10 times and add 10 different times (otherwise average and best should be same?)
def kem_bench(kem_test_iterations = 1, repetitions = 2):
    print("{:<20s} {:<20s} {:<20s} {:<20s} {:<20s}".format("Operation", "Total time (s)", "Average (s)", "Best (s)",
                                                           "Std.dev (s)"))

    titles = ["   Key generation: ", "KEM encapsulation: ", "KEM decapsulation: "]
    functions = [crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec]

    for fun, tl in zip(functions, titles):
        res = Timer(lambda: fun(), 'gc.enable()').repeat(repeat=repetitions, number=kem_test_iterations)
        print(tl+5 * " " + "{:<20s} {:<20s} {:<20s} {:<20s}".format(str(round(sum(res), 3)), str(round(mean(res), 3)),
                                                                    str(round(min(res), 3)), str(round(stdev(res), 3))))
#


def main():
    OK = kem_test(FrodoAPI640.CRYPTO_ALGNAME)

    if OK is True:
        kem_bench()

    exit(0)