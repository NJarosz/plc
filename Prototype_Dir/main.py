import time
import csv
from datetime import date, timedelta, datetime
from mfrc522 import SimpleMFRC522
from Prototype_Dir import I2C_LCD_driver
from gpiozero import LED, Button, OutputDevice
import os
import mfrc522
from datetime import datetime
import sys
from hardware import Hardware
from config import *

trigger_count = 1



file_path = ""

mode = modes["load"]
startup = True

# LCD Messages
csv_msg = "Updating CSV"
load_program_msg = "Loading Program"
load_part_msg = "Loading Part Info"
load_emp_msg = "Loading Emp Info"
load_count_msg = "Loading Count"
loading_msg = "Loading Info..."
invalid_data_msg = "Invalid Data"
invalid_program_top = "Invalid Seq"
invalid_program_btm = "Grn=Try Again"
menu_msg_top = "Reset Counter?"
menu_msg_btm = "Gr=Yes Red=No"
reset_count_msg = "Counter= 0"
logoutm = "Logged Out"
timeoutm = "Timed Out"
standby_dots = "...."
boot_time = datetime.now()
employees_loaded = False


# Functions

def read_totalcount():
    cnt = 0

    try:
        with open(TOTALCOUNT_FILE, "r") as cntfile:
            cntstr = cntfile.readline().rstrip("\n")
            cntstr = cntstr.strip()

            try:
                cnt = int(cntstr)
            except:
                pass
    except:
        pass

    if cnt < 0:
        cnt = 0

    if cnt > DEFAULT_COUNT_STOP:
        cnt = DEFAULT_COUNT_STOP

    return cnt


def ret_emp_name(id_num):
    emp_name = None

    if employees_loaded:
        try:
            emp_name = employees[emp_num]
        except:
            pass

    return emp_name


def update_count_file(totalcount):
    try:
        with open(TOTALCOUNT_FILE, "w", newline="") as cntfile:
            cntfile.write(str(totalcount))
    except:
        pass

    file_modify_time = get_file_modify_time(TOTALCOUNT_FILE)

    return file_modify_time


def potential_reboot():
    timenow = datetime.now()

    if timenow > boot_time + timedelta(seconds=REBOOT_WAIT_SECONDS) and timenow.hour == REBOOT_HOUR:
        lcd.clear()
        lcd.message("Rebooting ...        ", 1)
        os.system("sudo reboot")



def display_run_info(last_display, last_disp_time, logon_time):
    lcd.message(run_msg_btm, 2)
    now = datetime.now()
    if now > last_disp_time + timedelta(seconds=1):

        delta = now - logon_time
        delta_string = str(delta)

        name_length = 8
        delta_start = 0

        if delta_string[0:1] == "0":
            name_length = 10
            delta_start = 2

        this_msg = run_msg_top2 + "                    "
        last_display = 0

        this_msg = this_msg[0:name_length] + " " + delta_string[delta_start:7]

        lcd.message(this_msg, 1)
        last_disp_time = datetime.now()

    return last_display, last_disp_time


def change_msg(msg, sec=1, line=1):
    lcd.clear()
    lcd.message(msg, line)
    time.sleep(sec)


def logout_func(file_path):
    add_timestamp(LOGOUT, file_path)
    change_msg(logoutm, sec=1)


def get_file_modify_time(file_name):
    file_modify_time = -1

    try:
        file_modify_time = os.path.getmtime(file_name)
    except:
        pass

    return file_modify_time


def exit_and_reload():
    # this will exit the program  and the loop
    # inside of rc.local will restart it
    # this will clean up memory
    # previously we just reset the mode to "load"
    lcd.clear()
    lcd.message(loading_msg, 1)
    exit()


def write_card():
    lcd.clear()
    lcd.message("Begin Writing", 1)
    time.sleep(3)

    write_str = ''

    try:
        with open(WRITER_FILE, "r") as writefile:
            write_str = writefile.readline().rstrip("\n")
            write_str = write_str.strip()

    except:
        amsg = "File Open Error         "

    lcd.clear()

    if write_str != '':
        amsg = write_str + "                  "
        lcd.message(write_str, 1)
        lcd.message("B=Write R=Skip        ", 2)
        but_pressed = ''

        while but_pressed == '':
            if button1.is_pressed:
                but_pressed = 'R'

            if button2.is_pressed:
                but_pressed = 'B'

        if but_pressed == "R":
            lcd.clear()
            lcd.message("Write Cancelled      ", 1)
        else:
            lcd.message("Enter Card           ", 2)
            reader.write(write_str)
            lcd.message("Card Written         ", 2)

    else:
        lcd.message("Error Writing      ", 1)
        lcd.message(amsg, 2)

    time.sleep(5)


def read_main():
    """reads main to determine which
    file to read to create sequence"""

    with open(MAIN_PROGRAM_NAME, 'r') as m:
        txt = m.readline().rstrip("\n")

    return txt


def gpio_on(pin):
    pin.on()


def gpio_off(pin):
    pin.off()


def invalid_main():
    lcd.clear()
    lcd.message("FATAL ERROR", 1)
    lcd.message("INVALID MAIN", 2)


def invalid_sequence_file():
    lcd.clear()
    lcd.message("FATAL ERROR", 1)
    lcd.message("INVALID PGM FILE", 2)



def invalid_sequence(amsg):
    lcd.clear()
    lcd.message("INVALID SEQUENCE", 1)
    lcd.message(amsg, 2)



try:

    while True:
        if mode == modes["error"]:
            time.sleep(600)

        if mode == modes["load"]:

            lcd.clear()

            lcd.message(loading_msg, 1)

            # when starting up will create a csv (if needed)
            if startup is True:
                today, file_path = update_csv()
                startup = False

            # when date changes (at midnight) will create a new csv
            if date.today() != today:
                today, file_path = update_csv()

            try:
                program_filename = read_main()
                main_file_modify_time = get_file_modify_time(MAIN_PROGRAM_NAME)
            except:
                invalid_main()
                exit(1)

            # Set program_filename to the full path
            program_filename = PROGRAM_FOLDER + program_filename.strip()

            # Load the sequence
            try:
                seq = create_sequence(program_filename)
                program_file_modify_time = get_file_modify_time(program_filename)
            except:
                invalid_sequence_file()
                exit(1)

            if not evaluate_seq(seq, relays):
                exit(1)

            # upload the employee info into a list
            # if it fails we will not be able to display employee
            # names when they sign in
            try:
                employees = load_employee_list()
                employees_loaded = True

            except:
                lcd.clear()
                lcd.message("ERROR LOADING", 1)
                lcd.message("EMPLOYEES", 2)
                time.sleep(5)
                employees_loaded = False

            # get the current total count from a file
            # if it fails it will be set to zero
            total_count = read_totalcount()

            # get part number, machine number and counter stop_point
            part_num, mach_num, counter_stop_point = read_production_info()

            # initialze variables before going into standby mode
            emp_name = None
            emp_num = None
            idn = None
            standby_dots = "...."

            production_file_modify_time = get_file_modify_time(PRODUCTION_INFO_FILE)
            employee_file_modify_time = get_file_modify_time(EMPLOYEE_INFO_FILE)
            totalcount_file_modify_time = get_file_modify_time(TOTALCOUNT_FILE)

            last_load_time = datetime.now()
            mode = modes["standby"]

            time.sleep(5)

        if mode == modes["standby"]:

            lcd.clear()

            standby_info_top = f"{part_num}"

            standby_info_btm = f"{total_count}"

            if counter_stop_point != DEFAULT_COUNT_STOP:
                standby_info_btm = standby_info_btm.strip() + "/" + f"{counter_stop_point}"

            add_spaces = MAX_DISPLAY_LEN - (len(standby_info_btm) + len(mach_num))

            if add_spaces > 0:
                standby_info_btm = standby_info_btm + " " * add_spaces + mach_num
            else:
                standby_info_btm = standby_info_btm + " " * 16

            lcd.message(standby_info_top, 1)
            lcd.message(standby_info_btm, 2)

            while mode == modes["standby"]:
                if rfid_bypass.is_pressed:
                    if bypass_message:
                        standby_info_top = part_num + "                           "
                        bypass_message = False
                    else:
                        standby_info_top = part_num + " BYPASS" + "                "
                        bypass_message = True

                    lcd.message(standby_info_top, 1)
                    time.sleep(.5)
                else:

                    reader.READER.spi.close()
                    del reader
                    time.sleep(.5)
                    reader = SimpleMFRC522()

                    idn, emp_num = reader.read_no_block()

                    if emp_num != None:
                        emp_num = emp_num.strip()

                        if emp_num == '':
                            pass
                        else:
                            emp_name = ret_emp_name(emp_num)
                            emp_count = 0
                            add_timestamp(LOGON, file_path)
                            mode = modes["run"]
                    else:
                        if len(standby_dots) >= 3:
                            standby_dots = ""
                        else:
                            standby_dots = standby_dots + "."

                            standby_info_top = part_num + " " + standby_dots + "                "
                            lcd.message(standby_info_top, 1)
                            time.sleep(.1)

                if mode == modes["standby"] and button2.is_pressed:

                    if rfid_bypass.is_pressed:
                        button2.wait_for_release()
                        emp_num = 998
                        emp_name = ret_emp_name(emp_num)
                        emp_count = 0
                        add_timestamp(LOGON, file_path)
                        mode = modes["run"]
                    else:
                        lcd.message("Hold 3 sec>>Load", 1)
                        button_press_time = datetime.now()
                        button2.wait_for_release()

                        current_dt = datetime.now()

                        if current_dt >= button_press_time + timedelta(seconds=8):
                            write_card()
                            exit_and_reload()

                        elif datetime.now() >= button_press_time + timedelta(seconds=2.5):
                            exit_and_reload()

                if mode == modes["standby"] and button1.is_pressed:
                    lcd.message("Hold 3 sec>>Menu", 1)
                    button_press_time = datetime.now()
                    button1.wait_for_release()

                    if datetime.now() >= button_press_time + timedelta(seconds=2.5):
                        mode = modes["menu"]

                if mode == modes["standby"] and datetime.now() >= last_load_time + timedelta(seconds=RELOAD_SECONDS):

                    # determine if we need to reboot and if so will start a reboot
                    potential_reboot()

                    # get the modified time of the producation file
                    file_time = get_file_modify_time(PRODUCTION_INFO_FILE)

                    # if the file has been modifid change mode to load
                    if file_time != production_file_modify_time:
                        exit_and_reload()

                    # get the modified time of the employee file
                    file_time = get_file_modify_time(EMPLOYEE_INFO_FILE)

                    # if the file has been modifid change mode to load
                    if file_time != employee_file_modify_time:
                        exit_and_reload()

                    # get the modified time of the total count file
                    file_time = get_file_modify_time(TOTALCOUNT_FILE)

                    # if the file has been modifid change mode to load
                    if file_time != totalcount_file_modify_time:
                        exit_and_reload()

                    file_time = get_file_modify_time(MAIN_PROGRAM_NAME)

                    # if the file has been modifid change mode to load
                    if file_time != main_file_modify_time:
                        exit_and_reload()

                    file_time = get_file_modify_time(program_filename)

                    # if the file has been modifid change mode to load
                    if file_time != program_file_modify_time:
                        exit_and_reload()

                    last_load_time = datetime.now()

        elif mode == modes["menu"]:
            lcd.clear()
            time.sleep(.5)

            lcd.message(menu_msg_top, 1)
            lcd.message(menu_msg_btm, 2)

            while mode == modes["menu"]:
                if button2.is_pressed:
                    button2.wait_for_release()
                    total_count = 0
                    totalcount_file_modify_time = update_count_file(total_count)
                    change_msg(reset_count_msg, sec=3)
                    exit_and_reload()

                if button1.is_pressed:
                    button1.wait_for_release()
                    exit_and_reload()


        elif mode == modes["run"]:

            run_msg_top1 = part_num

            if emp_name != None:
                run_msg_top2 = f"{emp_name}"
            else:
                run_msg_top2 = f"{emp_num}"

            last_display = 0
            last_disp_time = datetime.now()
            logon_time = last_disp_time

            # initialize last_shot_run_time  to current datetime
            last_shot_run_time = datetime.now()

            lcd.clear()
            lcd.message(run_msg_top2, 1)

            while mode == modes["run"]:
                run_msg_btm = f"{emp_count}   {total_count}"

                if counter_stop_point != DEFAULT_COUNT_STOP:
                    run_msg_btm = run_msg_btm.strip() + "/" + f"{counter_stop_point}"

                last_display, last_disp_time = display_run_info(last_display, last_disp_time, logon_time)

                if total_count >= counter_stop_point:
                    logout_func(file_path)

                    total_count = 0
                    totalcount_file_modify_time = update_count_file(total_count)

                    lcd.clear()
                    lcd.message("Count Reached", 1)
                    lcd.message("Press Red Btn", 2)
                    button1.wait_for_press()
                    button1.wait_for_release()
                    exit_and_reload()

                if datetime.now() >= last_shot_run_time + timedelta(seconds=1):

                    run_shot = False

                    if trigger_count == 2:
                        if trigger_2.is_pressed & trigger_1.is_pressed:
                            run_shot = True
                    else:
                        if trigger_1.is_pressed:
                            run_shot = True

                    if run_shot:

                        emp_count += 1
                        total_count += 1
                        totalcount_file_modify_time = update_count_file(total_count)
                        add_timestamp(SHOT, file_path)
                        run_sequence(seq_dict=seq)
                        last_shot_run_time = datetime.now()

                        if trigger_count == 2:
                            if trigger_2.is_pressed:
                                trigger_2.wait_for_release()
                        else:
                            if trigger_1.is_pressed:
                                trigger_1.wait_for_release()

                if datetime.now() >= last_shot_run_time + timedelta(seconds=TIMEOUT_SECONDS):
                    add_timestamp(TIMEOUT, file_path)
                    change_msg(timeout_msg, sec=5)
                    exit_and_reload()

                if button1.is_pressed:
                    button1.wait_for_release()
                    logout_func(file_path)
                    exit_and_reload()


except KeyboardInterrupt:
    lcd.clear()
except Exception as e:
    lcd.clear()
    lcd.message("ERROR")
    print(e)
    time.sleep(5)