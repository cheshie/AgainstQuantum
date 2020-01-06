from timeit import Timer
from numpy import array_equal
from statistics import mean, stdev
from threading import Thread
import os
from time import sleep
from datetime import datetime
from enum import Enum


def get_system(system):
    global FrodoAPI
    global crypto_kem_keypair
    global crypto_kem_enc
    global crypto_kem_dec
    global set_public_key
    global set_secret_key
    global set_ciphertext

    if system is 'Frodo640':
        from FrodoKEM.frodo640.api_frodo640 import FrodoAPI640
        FrodoAPI = FrodoAPI640()
        crypto_kem_keypair = FrodoAPI.crypto_kem_keypair_frodo640
        crypto_kem_enc = FrodoAPI.crypto_kem_enc_frodo640
        crypto_kem_dec = FrodoAPI.crypto_kem_dec_frodo640
        set_public_key = FrodoAPI.kem.set_public_key
        set_secret_key = FrodoAPI.kem.set_secret_key
        set_ciphertext = FrodoAPI.kem.set_ciphertext
    elif system is 'Frodo976':
        pass
    elif system is 'Frodo1344':
        pass
    else:
        print("No such system. Exiting.")
        exit()
#


def kem_test(named_parameters, iterations=5, system='Frodo640'):
    get_system(system)

    def frodo_tester():
        global correct; correct = 0
        global incorrect; incorrect = 0
        global iteration_time; iteration_time = 0
        global current_operation; current_operation = 0

        start_time = datetime.now()
        for x in range(iterations):
            crypto_kem_keypair()
            current_operation += 1
            c, ss_encap = crypto_kem_enc()
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

        # Wait for main function to retrieve data from thread before it dies
        sleep(0.5)
    #

    def print_title_table():
        title = f"Testing correctness of key encapsulation mechanism (KEM), system {named_parameters}," \
                f" tests for {iterations} iterations\n"
        table = (len(title) - 1) * "=" + "\n"
        print(table + title + table)
    #

    def draw_bar(progress, length=20):
        print("[" + "#" * int(progress * length) + (length - int(progress * length)) * ' ' + ']',
              "(" + str(int(progress * 100)) + "%)")
    #

    def print_stats():
        class Operations(Enum):
            keyGeneration = 0
            keyEncapsulation = 1
            keyDecapsulation = 2
        #
        print(f"Time started: {time_started}\n", end="")
        if iteration_time > 0:
            print(f"Estimated time: {int(iteration_time * (iterations - incorrect - correct))} seconds\n", end="")
        print(f"Current operation: {str(Operations(current_operation))[len('Operations.'):]}\n", end="")
        print(f"Current iteration: {incorrect+correct}\n", end="")
        print(f"Correct results: {correct}\n", end="")
        print(f"Incorrect results: {incorrect}\n", end="")
    #

    test_thread = Thread(target=frodo_tester)
    test_thread.start()
    time_started = datetime.now()

    while test_thread.is_alive():
        _ = os.system("clear")
        print_title_table()
        print_stats()
        draw_bar((incorrect + correct) / iterations)
        sleep(0.5)
    #

    # Thread synchronization
    test_thread.join()
    time_finished = datetime.now()

    print("Tests finished.\n")
    print("Time finished: ", time_finished)
    print("Testing time: ", round((time_finished - time_started).total_seconds(), 2), "seconds")
    return True
#


def kem_bench(kem_test_iterations=1, repetitions=2, system='Frodo640'):
    get_system(system)

    print("{:<20s} {:<20s} {:<20s} {:<20s} {:<20s}".format("Operation", "Total time (s)", "Average (s)", "Best (s)",
                                                           "Std.dev (s)"))

    titles = ["   Key generation: ", "KEM encapsulation: ", "KEM decapsulation: "]
    functions = [crypto_kem_keypair, crypto_kem_enc, crypto_kem_dec]

    for frodo_op, tl in zip(functions, titles):
        res = Timer(lambda: frodo_op(), 'gc.enable()').repeat(repeat=repetitions, number=kem_test_iterations)
        print(tl+5 * " " + "{:<20s} {:<20s} {:<20s} {:<20s}".format(str(round(sum(res), 3)), str(round(mean(res), 3)),
                                                                    str(round(min(res), 3)), str(round(stdev(res), 3))))
#


def main():
    OK = kem_test(FrodoAPI.kem.CRYPTO_ALGNAME)

    if OK is True:
        kem_bench()

    exit(0)