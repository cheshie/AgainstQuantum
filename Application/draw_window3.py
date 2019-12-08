import curses
import curses.textpad
import readline

screen = curses.initscr()

import curses
from curses.textpad import Textbox, rectangle

"""
TODO: GREAT - THIS TEXTBX IS FUCKING POOR
Maybe use comnbination of simpple ascii tables ---- and python input() method? Would make it much simpler

"""

# def my_raw_input(stdscr, r, c, prompt_string):
#     curses.echo()
#     stdscr.addstr(r, c, prompt_string)
#     stdscr.refresh()
#     input = stdscr.getstr(r + 1, c, 20)
#     return input  #       ^^^^  reading input at next line
#
# if __name__ == "__main__":
#     stdscr = curses.initscr()
#     stdscr.clear()
#     choice = my_raw_input(stdscr, 2, 3, "cool or hot?").lower()
#     if choice == "cool":
#         stdscr.addstr(5,3,"Super cool!")
#     elif choice == "hot":
#         stdscr.addstr(5, 3," HOT!")
#     else:
#         stdscr.addstr(5, 3," Invalid input")
#     stdscr.refresh()
#     stdscr.getch()
#     curses.endwin()
def myvalid(a):
    pass
    # if a in [curses.KEY_ENTER, ord('\n'), 10]:
    #     return True

def main(stdscr):
    stdscr.addstr(0, 0, "Enter IM message: (hit Ctrl-G to send):")
    k = 0
    while k != ord('q'):
        editwin = curses.newwin(5,30, 2,1)
        editwin.box()
        # putwin = curses.newwin(5, 30, 8, 0)
        rectangle(stdscr, 1,0, 1+5+1, 1+30+1)
        if 32 < k < 120:
            editwin.addstr(1,1,chr(k))

        editwin.refresh()

        k = stdscr.getch()

    # rectangle(stdscr, 8, 0, 1 + 5 + 1 + 8, 1 + 30 + 1)
    # stdscr.refresh()
    # curses.echo()
    # editwin.box()
    # editwin.addstr(1,1, "dasdasdas")
    # stdscr.getch()

    # box = Textbox(editwin)


    # Let the user edit until Ctrl-G is struck.
    # box.edit()#myvalid)
    #
    # Get resulting contents
    # message = box.gather()

    # putwin.addstr(1, 1, message)

try:
    main(screen)
finally:
    curses.nocbreak()
    curses.echo()
    curses.endwin()


# # don't echo key strokes on the screen
# curses.noecho()
# # read keystrokes instantly, without waiting for enter to ne pressed
# curses.cbreak()
# # enable keypad mode
# stdscr.keypad(1)
# stdscr.clear()
# stdscr.refresh()
# win = curses.newwin(5, 60, 5, 10)
# tb = curses.textpad.Textbox(win)
# text = tb.edit()
# curses.beep()
# win.addstr(4,1,str.encode(text))

# def maketextbox(h,w,y,x,value="",deco=None,underlineChr=curses.ACS_HLINE,textColorpair=0,decoColorpair=0):
#     nw = curses.newwin(h,w,y,x)
#     txtbox = curses.textpad.Textbox(nw)
#     if deco=="frame":
#         screen.attron(decoColorpair)
#         curses.textpad.rectangle(screen,y-1,x-1,y+h,x+w)
#         screen.attroff(decoColorpair)
#     elif deco=="underline":
#         screen.hline(y+1,x,underlineChr,w,decoColorpair)
#
#     nw.addstr(0,0,value,textColorpair)
#     nw.attron(textColorpair)
#     screen.refresh()
#     return txtbox
#
# foo = maketextbox(1,40, 10,20,"foo")
# foo.edit()
# text = foo.gather()
#
#
# all_msg  = curses.newwin(2, 4, 0, 0);
# all_msg.box()
# all_msg.addstr(1, 1, text)