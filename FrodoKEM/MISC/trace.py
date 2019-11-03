global debug_mode
debug_mode = True


def trace(*what_to_trace, end=None):
    if debug_mode is True:
        if end is None:
            print(*what_to_trace)
        else:
            print(*what_to_trace, end=end)
#


def tracelst(name, list=None):
    if debug_mode is True:
        if isinstance(name,str) and type(list) != None:
            print(name,"= [",end="")
            for x in list[:-1]:
                print(str(x) + ", ", end="")
            print(str(list[-1]), end="")
        else:
            print("tab", "= [", end="")
            for x in name[:-1]:
                print(str(x)+", ", end="")
            print(str(name[-1]), end="")
        print("]\n\n")
#