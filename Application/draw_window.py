import curses
# https://gist.github.com/claymcleod/b670285f334acd56ad1c


# TODO: if window is too small, it crashes

def draw_menu(stdscr):
    k = 0

    prompt = "ANS ?> "
    written = ""; written_arr = []
    published = []
    shapes = [stdscr]

    # Clear and refresh the screen for a blank canvas
    stdscr.clear(); stdscr.refresh()

    # Loop where k is the last character pressed
    while k != ord('q'):

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        curr_row_pos = 1
        publ_row_pos = 1

        if chr(k).isprintable():
            written += chr(k)

        if len(written) > width//3:
            written_arr.append(written)
            written = ""

        # Define boxes for all messages and current message (height, width, y, x)
        all_msg = curses.newwin(height-height//7, width, 0, 0); shapes.append(all_msg)
        user_msg = curses.newwin(height // 7, width, height - height // 7, 0); shapes.append(user_msg)

        # Draw these boxes
        all_msg.box()
        user_msg.box()

        # Add prompts for each
        all_msg.addstr(1, 1, prompt)
        user_msg.addstr(1, 1, prompt)

        if len(published):
            for row in published:
                all_msg.addstr(publ_row_pos, len(prompt) + 1, row)

        # If there is more than one line draw line by line
        if len(written_arr):
            for row in written_arr:
                user_msg.addstr(curr_row_pos, len(prompt) + 1, row)
                curr_row_pos += 1

        # If user written anything in last line, print it
        if len(written):
            user_msg.addstr(curr_row_pos, len(prompt) + 1, written)

        # If user pressed enter, publish message and delete current one
        if k in [curses.KEY_ENTER, ord('\n')]:
            for row in written_arr:
                published.append(row)
            published.append(written)
            written = ""; written_arr.clear()

        # Re-draw all shapes
        for obj in shapes:
            obj.refresh()

        # Wait for next input
        k = stdscr.getch()
#


def main():
    try:
        curses.wrapper(draw_menu)
    finally:
        curses.endwin()
#


if __name__ == "__main__":
    main()
#