#! /usr/bin/python3

#Importing modules
import curses
import time
import sqlite3
from OpenSSL import crypto
from datetime import datetime
import random
import os

#Global variable with menu items
main_menu= ("Load certificates", "List certificates", "Exit")

def draw_menu(stdscr, selected_idx): #{
    h, w = stdscr.getmaxyx()
    menu_sign = ("________    _______      _                   ",
                 "(       )   (  ____ \   ( (    /|   |\     /|",
                 "| () () |   | (    \/   |  \  ( |   | )   ( |",
                 "| || || |   | (__       |   \ | |   | |   | |",
                 "| |(_)| |   |  __)      | (\ \) |   | |   | |",
                 "| |   | |   | (         | | \   |   | |   | |",
                 "| )   ( |   | (____/\   | )  \  |   | (___) |",
                 "|/     \|   (_______/   |/    )_)   (_______)")

    stdscr.clear()
    for idx, menu in enumerate(menu_sign):
        stdscr.addstr(idx+3, w//2-len(menu)//2, menu)

    for idx, row in enumerate(main_menu):
        x = w//2 - len(row)//2
        y = h//2 - len(main_menu)//2 + idx
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)

    stdscr.refresh()
#}

#DRAW EXIT SCREEN

#def draw_exit_screen(stdscr):
#    h, w = stdscr.getmaxyx()
#    while 1:
#        key = stdscr.getch()
#        stdscr.clear()
#        stdscr.addstr(h//2+2, w//2-len(ask)//2, ask)
#        if key==curses.KEY_RIGHT and pos > 0:
#            std
#        elif key==curses.KEY_LEFT:

def load_certificates(c, path_to_dir): #{
    list_of_files = os.listdir(path_to_dir)
    if len(list_of_files) == 0:
        return 0
    else:
        test = 0
        for filename in list_of_files:
            print(filename)
            user = cert_reader(path_to_dir, filename)
            c.execute('insert into users values (?,?,?,?,?,?,?,?,?,?)', user)
        return 1
    
#}

def cert_reader(path_to_dir, path_to_file): #{
        #Load certificate from file as string
        file = open(path_to_dir + "/" + path_to_file, "r")
        cert_str = file.read()
        filename = path_to_file
        file.close()
        #Creating x509 object
        cert = crypto.load_certificate(crypto.FILETYPE_PEM,cert_str)
        #Parsing important information from object as tuple
        x509_subject = cert.get_subject()
        subject = x509_subject.get_components()
        #Creating a tuple which will be returned
        serial_num = cert.get_serial_number()
        notBefore = cert.get_notBefore().decode('UTF-8')
        notAfter = cert.get_notAfter().decode('UTF-8')
        C = subject[0][1].decode('UTF-8')
        ST = subject[1][1].decode('UTF-8')
        O = subject[2][1].decode('UTF-8')
        OU = subject[3][1].decode('UTF-8')
        CN = subject[4][1].decode('UTF-8')
        emailAddress = subject[5][1].decode('UTF-8')
        person = (serial_num, filename, notBefore, notAfter, C, ST, O, OU, CN, emailAddress)
        return person
#}

#def list_certificates(c, option):
#    for row in c.execute('select count (not_after) from users where not_after <' +  time):
#        print(row)
#    for row in c.execute('select * from users where not_after <' +  time):
#        print(row)


def main(stdscr): #{
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    current_row = 0
    draw_menu(stdscr, current_row)
    h, w = stdscr.getmaxyx()

    #db variable
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE TABLE users (serial_num int, file_name text, not_before text, not_after text, C text, ST text, O text, OU text, CN text, email text)')

    while 1:
        key = stdscr.getch()
        if key==curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key==curses.KEY_DOWN and current_row < 2:
            current_row += 1
        elif key==curses.KEY_ENTER or key in [10,13]:
            #text = "You have pressed {}".format(main_menu[current_row])
            #stdscr.clear()
            #stdscr.addstr(0, 0, text)
            #stdscr.refresh()
            #stdscr.getch()
            if current_row == 0:    #   Load certificates
                path_to_dir = "__some__path__"
                return_value = load_certificates(c, path_to_dir)
                stdscr.clear()
                stdscr.addstr(h//2, w//2, str(return_value))
                for idx, row in enumerate(c.execute('select * from users')):
                    stdscr.addstr(h//2-idx, w//3, str(row))
                stdscr.refresh()
                time.sleep(2)
            elif current_row == 1:  #   List certificates
                #list_certificates()
                time.sleep(0.1)
            elif current_row == 2:  #   exit 
                exit(1)
        draw_menu(stdscr, current_row)
#}

curses.wrapper(main)
