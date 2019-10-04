global debug_mode
debug_mode = True


def trace(*what_to_trace, end=None):
    if debug_mode is True:
        if end is None:
            print(*what_to_trace)
        else:
            print(*what_to_trace, end=end)
#


def tracelst(name, list):
    if debug_mode is True:
        if name == '':
            print("tab: ", end="")
        else:
            print(name,": ",end="")
        for x in list:
            print(str(x)+", ", end="")
        print("\n\n")
#