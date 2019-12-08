import curses
import threading
from curses import textpad
# https://gist.github.com/claymcleod/b670285f334acd56ad1c

def draw_user_input(stdscr):
    # Loop where k is the last character pressed
    k = 0
    written = ""
    written_arr = []
    prompt = "ANS ?> "
    height, width = stdscr.getmaxyx()

    while k != ord('q'):
        if k in [curses.KEY_ENTER, ord('\n'), 10, 13]:
            raise KeyboardInterrupt

        if chr(k).isprintable():
            written += chr(k)

        if len(written) > width // 3:
            written_arr.append(written)
            written = ""

        user_msg = curses.newwin(height // 7, width, height - height // 7, 0)

        # Draw these boxes
        user_msg.box()

        # Add prompts for each
        user_msg.addstr(1, 1, prompt)

        user_msg.refresh()

        # Wait for next input
        k = stdscr.getch()


# TODO: if window is too small, it crashes
def draw_menu(stdscr):
    # Standard startup. Probably don't need to change this
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(1)

    k = 0

    prompt = "ANS ?> "
    written = ""; written_arr = []
    published = []
    shapes = [stdscr]

    # Clear and refresh the screen for a blank canvas
    stdscr.clear(); stdscr.refresh()

    height, width = stdscr.getmaxyx()
    curr_row_pos = 1
    publ_row_pos = 1

    write_handler = threading.Thread(target=draw_user_input, args=(stdscr,))
    write_handler.start()

    # Loop where k is the last character pressed
    while True:
        if chr(k).isprintable():
            written += chr(k)

        if len(written) > width//3:
            written_arr.append(written)
            written = ""

        # Define boxes for all messages and current message (height, width, y, x)
        all_msg  = curses.newwin(height-height//7, width, 0, 0); shapes.append(all_msg)
        # user_msg = curses.newwin(height // 7, width, height - height // 7, 0); shapes.append(user_msg)
        # rect   = textpad.rectangle(stdscr, 5, 5, 10, 10)
        # txtbox = textpad.Textbox(all_msg)
        # RETUERED = txtbox.edit() # Ctrl+G returns text, can I make it enter? Also the getch does not work anymore
        # see link: https://stackoverflow.com/questions/4581441/edit-text-using-python-and-curses-textbox-widget


        # Draw these boxes
        all_msg.box()
        # user_msg.box()

        # Add prompts for each
        all_msg.addstr(1, 1, prompt)
        # user_msg.addstr(1, 1, prompt)

        # If user pressed enter, publish message and delete current one
        all_msg.addstr(1, 1, prompt)
        written = ""; written_arr.clear()

        # Re-draw all shapes
        for obj in shapes:
            obj.refresh()

        # Wait for next input
        # k = stdscr.getch()
        # txtbox.do_command(k)

    stdscr.keypad(0)
#


def main():
    try:
        curses.wrapper(draw_menu)
    finally:
        curses.nocbreak()

        curses.echo()
        curses.endwin()
#


if __name__ == "__main__":
    main()
#