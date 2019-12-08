import curses
import random
import string
# TODO: if window is too small, it crashes


class ChatManager:
    def __init__(self):
        self.stdscr = curses.initscr()
        self.prompt = '#'+''.join(random.choice(string.ascii_uppercase+string.digits) for i in range(4)) + " > "
        self.curr_msg_row_nr = 1
        self.publ_row_nr     = 1
        self.height, self.width = self.stdscr.getmaxyx()
        self.user_msg = None
        self.all_msg  = None
        self.current_user_prompt = ""

        # Standard startup. Probably don't need to change this
        # Clear and refresh the screen for a blank canvas
        curses.cbreak()
        curses.noecho()
        self.stdscr.clear()
        self.stdscr.refresh()
        self.stdscr.keypad(1)

        self.main_window()
    #

    def __del__(self):
        self.stdscr.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    #

    def get_user_message(self):
        self.user_msg = self.initialize_window(self.height // 7, self.width, self.height - self.height // 7, 0, True)
        current_message = ""

        while True:
            k = self.stdscr.getch()

            if k in [curses.KEY_ENTER, ord('\n'), 10, 13]:
                return current_message

            elif chr(k).isprintable():
                current_message += chr(k)

            if len(current_message):
                self.display_message(self.user_msg, current_message, self.curr_msg_row_nr)

            self.user_msg.refresh()
    #

    def main_window(self):
        self.all_msg = self.initialize_window(self.height - self.height // 7, self.width, 0, 0)

        while True:
            published = self.get_user_message()
            self.publ_row_nr = self.display_message(self.all_msg, published, self.publ_row_nr, self.prompt)
            self.all_msg.refresh()
    #

    def initialize_window(self, ht, wdh, ystart, xstart, is_user=False):
        handle = curses.newwin(ht, wdh, ystart, xstart)
        if is_user is True:
            handle.addstr(1, 1, self.prompt)
        handle.box()
        handle.refresh()
        return handle
    #

    def display_message(self, window, message, row_nr, usr_prompt=None):
        row_nr_temp = 0
        winh, winw  = window.getmaxyx()
        winw = winw - len(self.prompt) - 2
        winh = winh - 2

        if usr_prompt is not self.current_user_prompt and usr_prompt is not None:
            window.addstr(row_nr, 1, usr_prompt)

        if len(message) > winw:
            rows_msg = [message[i:i + winw] for i in range(0, len(message), winw)]
            for row in rows_msg:
                window.addstr(row_nr, len(self.prompt) + 1, row)
                row_nr += 1
        else:
            window.addstr(row_nr, len(self.prompt) + 1, message)
            row_nr += 1

        if usr_prompt is not None:
            self.current_user_prompt = usr_prompt

        return row_nr - row_nr_temp
    #


if __name__ == "__main__":
    ChatManager()
#