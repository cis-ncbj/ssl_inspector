#! /usr/bin/python3

#Importing modules
import curses
import time
import sqlite3
from OpenSSL import crypto
from datetime import datetime
import random as rd
import os


#Global variable with menu items
main_menu= ("Load certificates from directory", "Load certificates from database", "List certificates", "Test options", "Exit")
test_menu = ("Generate random users and add to database", "List random users", "Return to main menu")
exit_menu = ("Do you want to save database?","YES", "NO")

test_menu_sign = (
"______________________ ____________________    _____  ___________ _______   ____ ___  ",
"\__    ___/\_   _____//   _____/\__    ___/   /     \ \_   _____/ \      \ |    |   \ ",
"  |    |    |    __)_ \_____  \   |    |     /  \ /  \ |    __)_  /   |   \|    |   / ",
"  |    |    |        \/        \  |    |    /    Y    \|        \/    |    \    |  /  ",
"  |____|   /_______  /_______  /  |____|    \____|__  /_______  /\____|__  /______/   ",
"                   \/        \/                     \/        \/         \/           ")

menu_sign_1 = (
"  _________ _________.____      ",
" /   _____//   _____/|    |     ",
" \_____  \ \_____  \ |    |     ",
" /        \/        \|    |___  ",
"/_______  /_______  /|_______ \ ",
"        \/        \/         \/ ")

menu_sign_2 = ( r'''.___ _______    __________________________________________________________ __________  ''',
		r'''|   |\      \  /   _____/\______   \_   _____/\_   ___ \__    ___/\_____  \\______   \ ''',
		r'''|   |/   |   \ \_____  \  |     ___/|    __)_ /    \  \/ |    |    /   |   \|       _/ ''',
		r'''|   /    |    \/        \ |    |    |        //     \____|    |   /    |    \    |   \ ''',
		r'''|___\____|__  /_______  / |____|   /_______  / \______  /|____|   \_______  /____|_  / ''',
		r'''            \/        \/                   \/         \/                  \/       \/  ''')

#Drawing main menu function
def draw_menu(stdscr, selected_idx): #{
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    for idx, menu in enumerate(menu_sign_1):
        stdscr.addstr(idx+3, w//2-len(menu)//2, menu)
#
    for idx, menu in enumerate(menu_sign_2):
        stdscr.addstr(idx+10, w//2-len(menu)//2, menu)
#
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

#Drawing test menu function
def draw_test_menu(stdscr, selected_idx): #{
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    for idx, menu in enumerate(test_menu_sign):
        stdscr.addstr(idx+3, w//2-len(menu)//2, menu)
    for idx, row in enumerate(test_menu):
        x = w//2 - len(row)//2
        y = h//2 - len(test_menu)//2 + idx
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()
#}

#DRAW EXIT SCREEN
def draw_exit_menu(stdscr, selected_idx): #{
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addstr(h//2-2, w//2-len(exit_menu[0])//2, exit_menu[0])
    if selected_idx == 1:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(h//2+2, w//2-5, exit_menu[1])
        stdscr.attroff(curses.color_pair(1))
        stdscr.addstr(h//2+2, w//2+5, exit_menu[2])
    else:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(h//2+2, w//2+5, exit_menu[2])
        stdscr.attroff(curses.color_pair(1))
        stdscr.addstr(h//2+2, w//2-5, exit_menu[1])
    stdscr.refresh()
#}

def exit_menu_fun(stdscr, conn, c): #{
    current_row = 1
    draw_exit_menu(stdscr, current_row)
    h, w = stdscr.getmaxyx()
    while 1:
        key = stdscr.getch()
        if key==curses.KEY_LEFT and current_row > 1:
            current_row -= 1
        elif key==curses.KEY_RIGHT and current_row < 2:
            current_row += 1
        elif key==curses.KEY_ENTER or key in [10,13]:
            if current_row == 1:
                break;
            elif current_row == 2:
                break;
        draw_exit_menu(stdscr, current_row)
    exit(1)
#}

#Loading data from ssl certificate
def cert_reader(stdscr, path_to_dir, path_to_file): #{
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
        #stdscr.addstr(1,1,person[1])
        return person
#}

#Loading certs from files
def load_certificates(stdscr, c, path_to_dir): #{
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    list_of_files = os.listdir(path_to_dir)
    if len(list_of_files) == 0:
        #stdscr.clear()
        text = "Failed to load certificates. [ PRESS ANY KEY ]"
        stdscr.addstr(h//2, w//2-len(text)//2, text)
        stdscr.getch()
    else:
        test = 0
        for filename in list_of_files:
            user = cert_reader(stdscr, path_to_dir, filename)
            c.execute('insert into users values (?,?,?,?,?,?,?,?,?,?)', user)
        #stdscr.clear()
        text = "Loaded certificates to database. [ PRESS ANY KEY ]"
        stdscr.addstr(h//2, w//2-len(text)//2, text)
        stdscr.getch()
  

#}

def gen_random_users(stdscr, conn, c, n): #{
    with open("names.txt", "r") as f_names:
        names = f_names.read().splitlines()
    with open("surnames.txt", "r") as f_surnames:
        surnames = f_surnames.read().splitlines()
    with open("states.txt", "r") as f_states:
        states = f_states.read().splitlines()
    for i in range(n):
        ser_num = i+1
        name = rd.choice(names)
        surname = rd.choice(surnames)
        emailAddress = name + "." + surname + "@" + rd.choice(["gmail.com", "onet.pl", "wp.pl", "random.mail.pl"])
        filename = name[0] + surname + ".crt"
        notBefore = str(rd.randint(2000,2009)) + "0" + str(rd.randint(1,9)) + str(rd.randint(10,29)) + "000000" + "Z"
        if rd.randint(0,100) < 50:
            notAfter = rd.randint(2010,2020)*pow(10,10) + 0 + rd.randint(1,9)*pow(10,8) + rd.randint(10,29)*pow(10,6) + 235959
        else:
            notAfter = 2020*pow(10,10) +  rd.randint(8,9)*pow(10,8) + rd.randint(10,29)*pow(10,6) + 235959
        C = "PL"
        ST = rd.choice(states)
        O = rd.choice(["PW", "PWr", "UW", "AGH", "UKSW", "PJATK"])
        OU = rd.choice(["Elektronika", "Informatyka", "Telekomunikacja", "Bioinformatyka", "Neuroinformatyka", "Teleinformatyka"])
        CN = name + " " + surname
        person = (ser_num, filename.lower(), notBefore, notAfter, C, ST, O, OU, CN, emailAddress.lower())
        c.execute('insert into users values (?,?,?,?,?,?,?,?,?,?)', person)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    txt = "Operation ended with success [ PRESS ANY KEY ]"
    stdscr.addstr(h//2, w//2-len(txt)//2, txt)
    stdscr.refresh()
    stdscr.getch()
#}

#20060618000000Z
def list_users(stdscr, users, pos, option): #{
    now = datetime.now()
    today = now.strftime("%Y%m%d%H%M%S")
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    serial_num = '{0:<5}'.format("SNUM")
    filename = '{0:<20}'.format("FILENAME")
    not_before = '{0:<15}'.format("NOT BEFORE")
    not_after = '{0:<14}'.format("NOT AFTER")
    C = '{0:<4}'.format("C")
    ST = '{0:<20}'.format("STATE")
    O = '{0:<10}'.format("OBJECT")
    OU = '{0:<18}'.format("OBJECT UNIT")
    CN = '{0:<25}'.format("NAME SURNAME")
    email = '{0:<30}'.format("EMAIL ADDRESS")
    top = serial_num + filename + not_before + " " + not_after + " " + C + ST + O + OU + CN + email
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 1, top)
    stdscr.attroff(curses.color_pair(1))
    if len(users) == 0:
       warning = "Your database is empty. Fill it with random users, or load from files."
       warning2 = "[ press 'q' to quit ]"
       stdscr.addstr(h//2-1, w//2-len(warning)//2, warning) 
       stdscr.addstr(h//2+1, w//2-len(warning2)//2, warning2) 
    else:
        if len(users) == 1:
            var = 2
        else:
            var = len(users)
        for i in range(0,min(h,var)-1):
            serial_num = '{0:<5}'.format(users[pos+i][0])
            filename = '{0:<20}'.format(users[pos+i][1])
            not_before = users[pos+i][2]
            not_after = users[pos+i][3]
            C = '{0:<4}'.format(users[pos+i][4])
            ST = '{0:<20}'.format(users[pos+i][5])
            O = '{0:<10}'.format(users[pos+i][6])
            OU = '{0:<18}'.format(users[pos+i][7])
            CN = '{0:<25}'.format(users[pos+i][8])
            email = '{0:<30}'.format(users[pos+i][9])
            record = serial_num + filename + not_before + " " + not_after + " " + C + ST + O + OU + CN + email
            if option == 0:
                stdscr.addstr(i+1, 1, record)
            elif option == 1:
                if not_after > today:
                    stdscr.attron(curses.color_pair(2))
                    stdscr.addstr(i+1, 1, record)
                    stdscr.attroff(curses.color_pair(2))
                else:
                    stdscr.attron(curses.color_pair(3))
                    stdscr.addstr(i+1, 1, record)
                    stdscr.attroff(curses.color_pair(3))
            elif option == 2:
                if not_after < today:
                    stdscr.attron(curses.color_pair(3))
                    stdscr.addstr(i+1, 1, record)
                    stdscr.attroff(curses.color_pair(3))
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(h-1,1,"q - quit | up_arrow - up | down_arrow - down | e - show expired | c - color list | a - page up | z - page down" )
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()
#}

def list_users_fun(stdscr, conn, c): #{
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    users = []
    pos = 0
    option = 0
    for row in c.execute("select * from users"):
        users.append(row)
    #if len(users) > 0:
    #    stdscr.clear()
    #    stdscr.addstr(1,1,users[0][8])
    #    stdscr.refresh()
    #    time.sleep(2)
    list_users(stdscr, users, pos, option)
    while 1:
        prev_option = option
        key = stdscr.getch()
        if key==curses.KEY_UP and pos > 0:
            pos -= 1
        elif key==curses.KEY_DOWN and pos < len(users)-h+2:
            pos += 1
        elif key == 97 and pos > 0:
            pos -= h
        elif key == 122 and pos + h < len(users)-h+2:
            pos += h
        elif key == 99:
            if prev_option == 1:
                option == 0
            option = 1
            list_users(stdscr, users, pos, option) 
        elif key == 101:
            option = 2 
            list_users(stdscr, users, pos, option) 
        elif key == 113:
            break
        list_users(stdscr, users, pos, option)
#}

def test_menu_fun(stdscr, conn, c): #{
    current_row = 0
    draw_test_menu(stdscr, current_row)
    h, w = stdscr.getmaxyx()
    while 1:
        key = stdscr.getch()
        if key==curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key==curses.KEY_DOWN and current_row < 2:
            current_row += 1
        elif key==curses.KEY_ENTER or key in [10,13]:
            if current_row == 0: #	Generate random users
                gen_random_users(stdscr, conn, c, 1000)
            elif current_row == 1: #	List random users
                list_users_fun(stdscr, conn, c)
            elif current_row == 2: #	Return to main menu
                break
        draw_test_menu(stdscr, current_row)
#}

def main_menu_fun(stdscr, conn, c): #{
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    current_row = 0
    draw_menu(stdscr, current_row)
    h, w = stdscr.getmaxyx()
    while 1:
        key = stdscr.getch()
        if key==curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key==curses.KEY_DOWN and current_row < 4:
            current_row += 1
        elif key==curses.KEY_ENTER or key in [10,13]:
            if current_row == 0:    #   Load certificates from directory
                path_to_dir = "_path_to_dir_"
                load_certificates(stdscr , c, path_to_dir)
            elif current_row == 2:  #   List certificates
                list_users_fun(stdscr, conn, c)
            elif current_row == 3:  #   Enter Test menu
                test_menu_fun(stdscr, conn, c)
            elif current_row == 4:  #   exit 
                exit_menu_fun(stdscr, conn, c)
                #exit(1)
        draw_menu(stdscr, current_row)
#}

def main(stdscr): #{
    #db variable
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE TABLE users (serial_num int, file_name text, not_before text, not_after text, C text, ST text, O text, OU text, CN text, email text)')
    main_menu_fun(stdscr, conn, c)
#}

curses.wrapper(main)
