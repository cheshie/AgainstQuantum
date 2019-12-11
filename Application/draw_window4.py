import curses
import random
import string
# TODO: if window is too small, it crashes
# tODO: implement thread with a stack that receives messages and prints them

class ChatManager:
    def __init__(self):
        self.stdscr = curses.initscr()
        self.nick   = ''.join(random.choice(string.ascii_uppercase+string.digits) for i in range(4))
        self.prompt = lambda n: '#'+ str(n) + " > "
        self.curr_msg_row_nr = 1
        self.publ_row_nr     = 1
        self.height, self.width = self.stdscr.getmaxyx()
        self.user_msg_box = None
        self.all_msg_box  = None
        self.current_user_prompt = ""
        self.current_message = {"nick":self.nick, "msg":str()}

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
        self.user_msg_box = self.initialize_window(self.height // 7, self.width, self.height - self.height // 7, 0, True)
        self.current_message['msg'] = str()

        while True:
            k = self.stdscr.getch()

            if k in [curses.KEY_ENTER, ord('\n'), 10, 13]:
                return self.current_message

            if k in [curses.KEY_BACKSPACE]:
                self.current_message['msg'] = self.current_message['msg'][:-1]

            elif chr(k).isprintable():
                self.current_message['msg'] += chr(k)

            if len(self.current_message['msg']):
                self.display_message(self.user_msg_box, self.current_message.copy(), self.curr_msg_row_nr)

            self.user_msg_box.refresh()
    #

    def main_window(self):
        self.all_msg_box = self.initialize_window(self.height - self.height // 7, self.width, 0, 0)

        while True:
            published = self.get_user_message()
            self.publ_row_nr = self.display_message(self.all_msg_box, published, self.publ_row_nr, self.prompt)
            self.all_msg_box.refresh()
    #

    def initialize_window(self, ht, wdh, ystart, xstart, is_user=False):
        handle = curses.newwin(ht, wdh, ystart, xstart)
        if is_user is True:
            handle.addstr(1, 1, self.prompt(self.nick))
        handle.box()
        handle.refresh()
        return handle
    #

    def display_message(self, window, message, row_nr, usr_prompt=None):
        row_nr_temp = 0
        winh, winw  = window.getmaxyx()
        winw = winw - len(self.prompt(self.nick)) - 2
        winh = winh - 2

        # Heres the thing
        # do not separate prompt and message, the prompt should be a part of it
        # placed at the start.
        # If entire message is longer than etc. then display last part of it

        # if usr_prompt is not self.current_user_prompt and usr_prompt is not None:
            # window.addstr(row_nr, 1, usr_prompt)

        if row_nr >= winh:
            if len(message['msg']) > winw:
                window.clear(); window.box()
                rows_msg = [message['msg'][i:i + winw] for i in range(0, len(message['msg']), winw)][-winh:]

                window.addstr(row_nr, 1, self.prompt(message['nick']))
                for row in rows_msg:
                    window.addstr(row_nr, len(self.prompt(message['nick'])) + 1, row)
                    row_nr += 1
            else:
                window.addstr(row_nr, 1, self.prompt(message['nick']))
                window.addstr(row_nr, len(self.prompt(message['nick'])) + 1, message['msg'])
                row_nr += 1
        else:
            window.clear(); window.box()

        # if usr_prompt is not None:
        #     self.current_user_prompt = usr_prompt

        return row_nr - row_nr_temp
    #


if __name__ == "__main__":
    ChatManager()
#