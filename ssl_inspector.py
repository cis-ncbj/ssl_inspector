#! /usr/bin/python3

# [x] Toggle list
# [x] Sorting list by everything
# [ ] Statistics
# [ ] Graphs
# [ ] ... ?

#Importing modules
import curses
import time
import sqlite3
from OpenSSL import crypto
from datetime import datetime
import random as rd
import os
from curses.textpad import rectangle
from operator import itemgetter


#Global variable with menu items
main_menu= ("Load certificates from directory", "Load certificates from database", "List certificates", "Test options", "Exit")
test_menu = ("Generate random users and add to database", "List random users", "Return to main menu")
exit_menu = ("Do you want to save database?","YES", "NO")
sort_menu = ("ID", "File name", "Not before", "Not after", "Country", "State", "Object", "Object unit", "Name", "Email Address")

test_menu_sign = (
                  "______________________ ____________________    _____  ___________ _______   ____ ___  ",
                  "\__    ___/\_   _____//   _____/\__    ___/   /     \ \_   _____/ \      \ |    |   \ ",
                  "  |    |    |    __)_ \_____  \   |    |     /  \ /  \ |    __)_  /   |   \|    |   / ",
                  "  |    |    |        \/        \  |    |    /    Y    \|        \/    |    \    |  /  ",
                  "  |____|   /_______  /_______  /  |____|    \____|__  /_______  /\____|__  /______/   ",
                  "                   \/        \/                     \/        \/         \/           ")

menu_sign_1 = (
"                     $$\       $$\                                                     $$\                          ",
"                     $$ |      \__|                                                    $$ |                         ",
"  $$$$$$$\  $$$$$$$\ $$ |      $$\ $$$$$$$\   $$$$$$$\  $$$$$$\   $$$$$$\   $$$$$$$\ $$$$$$\    $$$$$$\   $$$$$$\   ",
" $$  _____|$$  _____|$$ |      $$ |$$  __$$\ $$  _____|$$  __$$\ $$  __$$\ $$  _____|\_$$  _|  $$  __$$\ $$  __$$\  ",
" \$$$$$$\  \$$$$$$\  $$ |      $$ |$$ |  $$ |\$$$$$$\  $$ /  $$ |$$$$$$$$ |$$ /        $$ |    $$ /  $$ |$$ |  \__| ",
"  \____$$\  \____$$\ $$ |      $$ |$$ |  $$ | \____$$\ $$ |  $$ |$$   ____|$$ |        $$ |$$\ $$ |  $$ |$$ |       ",
" $$$$$$$  |$$$$$$$  |$$ |      $$ |$$ |  $$ |$$$$$$$  |$$$$$$$  |\$$$$$$$\ \$$$$$$$\   \$$$$  |\$$$$$$  |$$ |       ",
" \_______/ \_______/ \__|      \__|\__|  \__|\_______/ $$  ____/  \_______| \_______|   \____/  \______/ \__|       ",
"                                                       $$ |                                                         ",
"                                                       $$ |                                                         ",
"                                                       \__|                                                         ")

#Drawing main menu function
def draw_menu(stdscr, selected_idx): #{
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    for idx, menu in enumerate(menu_sign_1):
        stdscr.addstr(idx+5, w//2-len(menu)//2, menu)
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
        return person
#}

def draw_sort_menu(sortwin, pos, h, w): #{
    sortwin.clear()
    sortwin.border()
    sort = "Sort by"
    sortwin.addstr(0,w//2-len(sort)//2,sort, curses.color_pair(1))
    for idx, menu in enumerate(sort_menu):
        if idx == pos:
            sortwin.attron(curses.color_pair(1))
            sortwin.addstr(idx+2,w//2-len(menu)//2, menu)    
            sortwin.attroff(curses.color_pair(1))
        else:
            sortwin.addstr(idx+2,w//2-len(menu)//2, menu)    
    sortwin.refresh()
#}
    

def sort_menu_fun(stdscr, users): #{
    h, w = stdscr.getmaxyx()
    sortwin = curses.newwin(15, 40, h//2-10, w//2-20)
    h, w = sortwin.getmaxyx()
    pos = 0 
    #stdscr.attron(curses.color_pair(3))
    #sortwin.bkgd(curses.color_pair(2))
    #sortwin.erase()
    draw_sort_menu(sortwin, pos, h, w)
    while True:
        key = stdscr.getch()
        if key==curses.KEY_UP and pos > 0:
            pos -= 1
        elif key==curses.KEY_DOWN and pos < len(sort_menu)-1:
            pos += 1
        elif key==curses.KEY_ENTER or key in [10,13]:
            if pos == 0:
                users.sort(key=itemgetter(0))
            elif pos == 1:
                users.sort(key=itemgetter(1))
            elif pos == 2:
                users.sort(key=itemgetter(2))
            elif pos == 3:
                users.sort(key=itemgetter(3))
            elif pos == 4:
                users.sort(key=itemgetter(4))
            elif pos == 5:
                users.sort(key=itemgetter(5))
            elif pos == 6:
                users.sort(key=itemgetter(6))
            elif pos == 7:
                users.sort(key=itemgetter(7))
            elif pos == 8:
                users.sort(key=itemgetter(8))
            elif pos == 9:
                users.sort(key=itemgetter(9))
            break
        draw_sort_menu(sortwin, pos, h, w)
#}

#Gathering user input with path to directory with certs
def load_certs_input(stdscr, c): #{
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    info = "Enter path to directory with certificates [to end press Ctrl-G or ENTER ]:"
    stdscr.addstr(h//2-10, w//2-len(info)//2, info)
    editwin = curses.newwin(1,100, h//2-5, w//2-50)
    rectangle(stdscr, h//2-6, w//2-51, h//2-4, w//2+50)
    stdscr.refresh()
    box = curses.textpad.Textbox(editwin)
    # Let the user edit until Ctrl-G is struck.
    box.edit()
    # Get resulting contents
    message = box.gather()
    return message[:-1]
#}

def load_from_database_input(stdscr): #{
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    info = "Enter path to your database file [to end press Ctrl-G or ENTER]:"
    stdscr.addstr(h//2-10, w//2-len(info)//2, info)
    editwin = curses.newwin(1,100,h//2-5, w//2-50)
    rectangle(stdscr, h//2-6, w//2-51, h//2-4, w//2+50)
    stdscr.refresh()
    box = curses.textpad.Textbox(editwin)
    # Let the user edit until Ctrl-G is struck.
    box.edit()
    # Get resulting contents
    message = box.gather()
    return message[:-1]
#}

#Loading certs from database file (sqlite3)
def load_from_database(stdscr): #{
    h, w = stdscr.getmaxyx()
    path_to_db = load_from_database_input(stdscr)
    conn = sqlite3.connect(path_to_db)
    if not os.path.exists(path_to_db):
        text = "Failed to load certificates. [ PRESS ANY KEY ]"
        stdscr.addstr(h//2, w//2-len(text)//2, text)
        stdscr.getch()
    else:
        text = "Loaded certificates to database. [ PRESS ANY KEY ]"
        stdscr.addstr(h//2, w//2-len(text)//2, text)
        stdscr.getch()
        return conn
    

#Loading certs from files
def load_certificates(stdscr, c): #{
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    path_to_dir = load_certs_input(stdscr, c)
    if not os.path.exists(path_to_dir):
        text = "Failed to load certificates. [ PRESS ANY KEY ]"
        stdscr.addstr(h//2, w//2-len(text)//2, text)
        stdscr.getch()
    else:
        list_of_files = os.listdir(path_to_dir)
        for filename in list_of_files:
            user = cert_reader(stdscr, path_to_dir, filename)
            c.execute('insert into users values (?,?,?,?,?,?,?,?,?,?)', user)
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

#def draw_list_search_menu(sortwin, pos, h, w): #{
#    sortwin.clear()
#    sortwin.border()
#    sort = "Search in"
#    sortwin.addstr(0,w//2-len(sort)//2,sort, curses.color_pair(1))
#    for idx, menu in enumerate(sort_menu):
#        if idx == pos:
#            sortwin.attron(curses.color_pair(1))
#            sortwin.addstr(idx+2,w//2-len(menu)//2, menu)    
#            sortwin.attroff(curses.color_pair(1))
#        else:
#            sortwin.addstr(idx+2,w//2-len(menu)//2, menu)    
#    sortwin.refresh()
#}

#def list_search_input(stdscr): #{
#    h, w = stdscr.getmaxyx()
#    for i in range (10):
#        for j in range (110):
#            stdscr.addstr(h//2-(i+2), 55+w//2-(j), " ")
#    rectangle(stdscr, h//2-12, w//2-55, h//2-2, w//2+55)
#    info = "What are u looking for [to end press Ctrl-G or ENTER ]:"
#    stdscr.addstr(h//2-10, w//2-len(info)//2, info)
#    stdscr.refresh()
#    editwin = curses.newwin(1,100, h//2-5, w//2-50)
#    rectangle(stdscr, h//2-6, w//2-51, h//2-4, w//2+50)
#    stdscr.refresh()
#    box = curses.textpad.Textbox(editwin)
#    # Let the user edit until Ctrl-G is struck.
#    box.edit()
#    # Get resulting contents
#    message = box.gather()
#    return message[:-1]
#}

#def list_search_menu(stdscr, users): #{
#    h, w = stdscr.getmaxyx()
#    searchwin = curses.newwin(15, 40, h//2-10, w//2-20)
#    h, w = searchwin.getmaxyx()
#    pos = 0 
#    draw_list_search_menu(searchwin, pos, h, w)
#    while True:
#        key = stdscr.getch()
#        if key==curses.KEY_UP and pos > 0:
#            pos -= 1
#        elif key==curses.KEY_DOWN and pos < len(sort_menu)-1:
#            pos += 1
#        elif key==curses.KEY_ENTER or key in [10,13]:
#            if pos == 0:
#                return 0
#            elif pos == 1:
#                return 1
#            elif pos == 2:
#                return 2
#            elif pos == 3:
#                return 3
#            elif pos == 4:
#                return 4
#            elif pos == 5:
#                return 5
#            elif pos == 6:
#                return 6
#            elif pos == 7:
#                return 7
#            elif pos == 8:
#                return 8
#            elif pos == 9:
#                return 9
#        draw_list_search_menu(searchwin, pos, h, w)
#}

#def list_search(stdscr, users, pos, option):
#    h, w = stdscr.getmaxyx()
#    option = list_search_menu(stdscr, users)
#    list_users(stdscr, users, pos, option) 
#    pattern = list_search_input(stdscr)
#    pos = next((x for i, x in enumerate(users) if x == pattern), 0)
#    if pos == 0:
#        warning = curses.newwin(30, 100, h//2-15, w//2-15)
#        h_w, w_w = warning.getmaxyx()
#        text = "Couldn't find any item"
#        warning.addstr(h_w//2, w_w//2-len(text), text)
#        warning.getch()
#    return pos

#Gathering user input with path to directory with certs
def load_certs_input(stdscr, c): #{
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    info = "Enter path to directory with certificates [to end press Ctrl-G or ENTER ]:"
    stdscr.addstr(h//2-10, w//2-len(info)//2, info)
    editwin = curses.newwin(1,100, h//2-5, w//2-50)
    rectangle(stdscr, h//2-6, w//2-51, h//2-4, w//2+50)
    stdscr.refresh()
    box = curses.textpad.Textbox(editwin)
    # Let the user edit until Ctrl-G is struck.
    box.edit()
    # Get resulting contents
    message = box.gather()
    return message[:-1]
#}

def load_from_database_input(stdscr): #{
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    info = "Enter path to your database file [to end press Ctrl-G or ENTER]:"
    stdscr.addstr(h//2-10, w//2-len(info)//2, info)
    editwin = curses.newwin(1,100,h//2-5, w//2-50)
    rectangle(stdscr, h//2-6, w//2-51, h//2-4, w//2+50)
    stdscr.refresh()
    box = curses.textpad.Textbox(editwin)
    # Let the user edit until Ctrl-G is struck.
    box.edit()
    # Get resulting contents
    message = box.gather()
    return message[:-1]
#}

def load_from_database(stdscr): #{
    h, w = stdscr.getmaxyx()
    path_to_db = load_from_database_input(stdscr)
    conn = sqlite3.connect(path_to_db)
    if not os.path.exists(path_to_db):
        text = "Failed to load certificates. [ PRESS ANY KEY ]"
        stdscr.addstr(h//2, w//2-len(text)//2, text)
        stdscr.getch()
    else:
        text = "Loaded certificates to database. [ PRESS ANY KEY ]"
        stdscr.addstr(h//2, w//2-len(text)//2, text)
        stdscr.getch()
        return conn
    

#Loading certs from files
def load_certificates(stdscr, c): #{
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    path_to_dir = load_certs_input(stdscr, c)
    if not os.path.exists(path_to_dir):
        text = "Failed to load certificates. [ PRESS ANY KEY ]"
        stdscr.addstr(h//2, w//2-len(text)//2, text)
        stdscr.getch()
    else:
        list_of_files = os.listdir(path_to_dir)
        for filename in list_of_files:
            user = cert_reader(stdscr, path_to_dir, filename)
            c.execute('insert into users values (?,?,?,?,?,?,?,?,?,?)', user)
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
    #HEADLINE OF LIST
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
    top = serial_num + filename + not_before + " " + not_after + " " + C + ST + O + OU + CN + email + " " + str(pos) + " | " +  str(len(users))
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 1, top)
    stdscr.attroff(curses.color_pair(1))
#
    if len(users) == 0:
       warning = "Your database is empty. Fill it with random users, or load from files."
       warning2 = "[ press 'q' to quit ]"
       stdscr.addstr(h//2-1, w//2-len(warning)//2, warning) 
       stdscr.addstr(h//2+1, w//2-len(warning2)//2, warning2) 
    else:
        #if len(users) == 1:
        #    var = 2
        #else:
        #    var = len(users)
        for i in range(0,min(h,len(users))-2):
            if pos+i < len(users):
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
                #    if not_after < today:
                        #stdscr.attron(curses.color_pair(3))
                    stdscr.addstr(i+1, 1, record, curses.color_pair(3))
                        #stdscr.attroff(curses.color_pair(3))
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(h-1,1,"q - quit | up_arrow - up | down_arrow - down | e - show expired | c - color list | a - page up | z - page down | s - sort list " )
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()
#}

def list_users_fun(stdscr, conn, c): #{
    now = datetime.now()
    today = now.strftime("%Y%m%d%H%M%S")
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    users = []
    tmp_users = users
    expired_users = []
    option = 0
    color_on = False
    expired_on = False
    pos = 0
    for row in c.execute("select * from users"):
        users.append(row)
    for row in c.execute("select * from users where not_after < " +  today):
        expired_users.append(row)
    list_users(stdscr, users, pos, option)
    while 1:
        prev_option = option
        key = stdscr.getch()
        if key==curses.KEY_UP and pos > 0:
            pos -= 1
        elif key==curses.KEY_DOWN and pos < len(tmp_users)-h+2:
            pos += 1
        elif key == 97 and pos > 0:
            if pos < h-2:
                pos = 0
            else:
                pos -= h-2
        elif key == 122 :
            if  len(tmp_users)-pos+2 < 2*(h-2): 
                pos = len(tmp_users) - h + 2
            else:
                pos += h-2
        elif key == 99:
            tmp_users = users
            if color_on == True:
                color_on = False
                option = 0
            else:
                color_on = True
                option = 1
            list_users(stdscr, tmp_users, pos, option) 
        elif key == 101:
            pos = 0
            if expired_on == True:
                tmp_users = users
                expired_on = False
                option = 0
            else:
                tmp_users = expired_users
                expired_on = True
                color_on = False
                option = 2 
            list_users(stdscr, tmp_users, pos, option) 
        elif key == 113:
            break
        elif key == 115:
            pos = 0
            sort_menu_fun(stdscr, tmp_users)
        elif key == 47:
            list_search(stdscr, tmp_users, pos, option)
        list_users(stdscr, tmp_users, pos, option)
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
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)
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
                load_certificates(stdscr , c)
            elif current_row == 1:  #   Load database
                conn = load_from_database(stdscr)
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
