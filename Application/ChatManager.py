import curses
import json
import random
import string
import threading
from time import sleep
from Application.ConnectionManager import ConnectionManager

#from typing import Dict, Tuple, #TypedDict
# TODO: if window is too small, it crashes
# TODO: implement thread with a stack that receives messages and prints them
# TODO: cursos movement => back and forth and up to move around edited message

# Heres the thing
        # do not separate prompt and message, the prompt should be a part of it
        # placed at the start.
        # If entire message is longer than etc. then display last part of it

        # if usr_prompt is not self.current_user_prompt and usr_prompt is not None:
        # window.addstr(row_nr, 1, usr_prompt)

# def send_message(self, message):
#     self.archive += (message, )
#     # self.all_msg_box.refresh()
# #


class ChatManager:
    def __init__(self, mode='text'):
        self.nick   = ''.join(random.choice(string.ascii_uppercase+string.digits) for i in range(4))
        self.prompt = lambda n: '#'+ str(n) + " > "
        self.curr_msg_row_nr = 1
        self.publ_row_nr     = 1
        self.user_msg_box = None
        self.all_msg_box  = None
        self.current_user_prompt = ""
        self.current_message = {"nick": self.nick, "msg": str()}#Dict[{"nick":self.nick, "msg":str()}]
        self.archive = ()
        self.mode = mode
        self.connection = ConnectionManager(mode=self.mode)
        self.message_received = False

        # Standard setup. Probably don't need to change this
        # Clear and refresh the screen for a blank canvas
        if self.mode == 'visual':
            self.stdscr = curses.initscr()
            self.height, self.width = self.stdscr.getmaxyx()
            curses.cbreak()
            curses.noecho()
            self.stdscr.clear()
            self.stdscr.refresh()
            self.stdscr.keypad(1)
    #

    def __del__(self):
        if self.mode == 'visual':
            self.stdscr.keypad(0)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
    #

    def get_user_message(self):
        if self.mode == 'text':
            # Wait for other threads synchronization
            sleep(0.5)
            return {"nick": self.nick, "msg": input('\n' + self.prompt(self.nick))}

        self.user_msg_box = self.initialize_window(self.height // 7, self.width, self.height - self.height // 7, 0, True)
        self.current_message['msg'] = str()

        while True:
            k = self.stdscr.getch()

            if k in [curses.KEY_ENTER, ord('\n'), 10, 13]:
                # self.send_message(self.current_message)
                return self.current_message

            if k in [curses.KEY_BACKSPACE]:
                if len(self.current_message['msg']) > 1:
                    self.current_message['msg'] = self.current_message['msg'][:-1]
                    self.user_msg_box.clear();self.user_msg_box.box()
                else:
                    continue

            elif chr(k).isprintable():
                self.current_message['msg'] += chr(k)

            if len(self.current_message['msg']):
                self.display_message_current()

            self.user_msg_box.refresh()
    #

    def start_client(self):
        if self.mode == 'visual':
            self.all_msg_box = self.initialize_window(self.height - self.height // 7, self.width, 0, 0)
        self.connection.start_client(self)

        while True:
            message = self.get_user_message()
            self.connection.send_message(message)
            if self.mode == 'visual':
                self.display_message_main(message)
    #

    def start_server(self):
        if self.mode =='visual':
            self.all_msg_box = self.initialize_window(self.height - self.height // 7, self.width, 0, 0)

        self.connection.start_server(chatref=self)
    #

    def initialize_window(self, ht, wdh, ystart, xstart, is_user=False):
        handle = curses.newwin(ht, wdh, ystart, xstart)
        if is_user is True:
            handle.addstr(1, 1, self.prompt(self.nick))
        handle.box()
        handle.refresh()
        return handle
    #

    def display_message_main(self, message, reset=False):
        if self.mode == 'text':
            # If new message from server arrived, reset prompt for the local user
            if reset == True:
                ending = '\n' + self.prompt(self.nick)
            else:
                ending = str()

            # Display message and optionally prompt (True)
            print('\n' + self.prompt(message['nick']) + message['msg'] + ending, end="")
            return

        winh, winw = self.all_msg_box.getmaxyx()
        winw = winw - len(self.prompt(self.nick)) - 2
        winh = winh - 2
        # message = self.archive[-1]

        if self.publ_row_nr <= winh:
            if len(message['msg']) > winw:
                rows_msg = [message['msg'][i:i + winw] for i in range(0, len(message['msg']), winw)][-winh:]
                self.all_msg_box.addstr(self.publ_row_nr, 1, self.prompt(message['nick']))
                for row in rows_msg:
                    self.all_msg_box.addstr(self.publ_row_nr, len(self.prompt(message['nick'])) + 1, row)
                    self.publ_row_nr += 1
            else:
                self.all_msg_box.addstr(self.publ_row_nr, 1, self.prompt(message['nick']))
                self.all_msg_box.addstr(self.publ_row_nr, len(self.prompt(message['nick'])) + 1, message['msg'])
                self.publ_row_nr += 1
        else:
            self.all_msg_box.clear(); self.all_msg_box.box()
            self.publ_row_nr = 1

        self.all_msg_box.refresh()
    #

    def display_message_current(self):
        self.curr_msg_row_nr = 1
        winh, winw = self.user_msg_box.getmaxyx()
        winw = winw - len(self.prompt(self.nick)) - 2
        winh = winh - 2

        if self.curr_msg_row_nr <= winh:
            if len(self.current_message['msg']) > winw:
                self.user_msg_box.clear(); self.user_msg_box.box()
                rows_msg = [self.current_message['msg'][i:i + winw] for i in range(0, len(self.current_message['msg']), winw)][-winh:]

                self.user_msg_box.addstr(self.curr_msg_row_nr, 1, self.prompt(self.current_message['nick']))
                for row in rows_msg:
                    self.user_msg_box.addstr(self.curr_msg_row_nr, len(self.prompt(self.current_message['nick'])) + 1, row)
                    self.curr_msg_row_nr += 1
            else:
                self.user_msg_box.addstr(self.curr_msg_row_nr, 1, self.prompt(self.current_message['nick']))
                self.user_msg_box.addstr(self.curr_msg_row_nr, len(self.prompt(self.current_message['nick'])) + 1, self.current_message['msg'])
        else:
            self.user_msg_box.window.clear(); self.user_msg_box.window.box()
    #
#


if __name__ == "__main__":
    ChatManager()
