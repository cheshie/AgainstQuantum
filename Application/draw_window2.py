import curses
from curses import textpad
# https://gist.github.com/claymcleod/b670285f334acd56ad1c


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

    # Loop where k is the last character pressed
    while k != ord('q'):
        # if k in [curses.KEY_ENTER, ord('\n'), 10]:
            # continue

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        curr_row_pos = 1
        publ_row_pos = 1

        if len(published):
            all_msg.addstr(publ_row_pos, len(prompt) + 1, published)

        # if chr(k).isprintable():
        #     written += chr(k)
        #
        # if len(written) > width//3:
        #     written_arr.append(written)
        #     written = ""

        # Define boxes for all messages and current message (height, width, y, x)
        all_msg  = curses.newwin(height-height//7, width, 0, 0); shapes.append(all_msg)
        user_msg = curses.newwin(height // 7 - 1, width - 1, height - height // 7 + 1, 1)#; shapes.append(user_msg)
        # textpad.rectangle(stdscr, height // 7, width, height - height // 7, 0)
        # rect   = textpad.rectangle(stdscr, 5, 5, 10, 10)
        txtbox = textpad.Textbox(user_msg)

        # Draw these boxes
        all_msg.box()
        # user_msg.box()

        # Add prompts for each
        all_msg.addstr(1, 1, prompt); all_msg.refresh()
        # user_msg.addstr(1, 1, prompt)

        txtbox.edit() # Ctrl+G returns text, can I make it enter? Also the getch does not work anymore
        published = txtbox.gather()
        # see link: https://stackoverflow.com/questions/4581441/edit-text-using-python-and-curses-textbox-widget

        # if len(published):
        #     for row in published:
        #         all_msg.addstr(publ_row_pos, len(prompt) + 1, row)


        # Re-draw all shapes
        # for obj in shapes:
            # obj.refresh()

        # If there is more than one line draw line by line
        # if len(written_arr):
        #     for row in written_arr:
        #         user_msg.addstr(curr_row_pos, len(prompt) + 1, row)
        #         curr_row_pos += 1

        # If user written anything in last line, print it
        # if len(written):
        #     user_msg.addstr(curr_row_pos, len(prompt) + 1, written)

        # If user pressed enter, publish message and delete current one
        # if k in [curses.KEY_ENTER, ord('\n')]:
        #     for row in written_arr:
        #         published.append(row)
        #     published.append(written)
        #     written = ""; written_arr.clear()



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