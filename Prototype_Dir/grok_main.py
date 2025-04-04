# main.py
import sys
import time
import os
from datetime import datetime, timedelta, date
from hardware import Hardware
from sequence import create_sequence, evaluate_sequence, run_sequence
from file_io import load_employee_list, update_csv, add_timestamp, read_total_count, update_total_count, \
    get_file_modify_time, read_production_info
from ui import UI
from utils import write_card
from config import *


def potential_reboot():
    timenow = datetime.now()
    if timenow > boot_time + timedelta(seconds=REBOOT_WAIT_SECONDS) and timenow.hour == REBOOT_HOUR:
        ui.clear()
        ui.message("Rebooting ...", 1)
        os.system("sudo reboot")


def exit_and_reload():
    ui.clear()
    ui.message("Reloading ...", 1)
    exit()


def main():
    triggers = sys.argv[1].upper().strip() if len(sys.argv) > 1 else "default"
    hw = Hardware(triggers)
    ui = UI(hw.lcd)
    mode = MODES["load"]
    startup = True
    employees, employees_loaded = load_employee_list()
    total_count = read_total_count()
    emp_num, emp_name = None, None
    today, file_path = None, None
    logon_time = None
    boot_time = datetime.now()
    last_load_time = datetime.now()

    try:
        while True:
            if mode == MODES["load"]:
                ui.clear()
                ui.message("Loading Info...", 1, 5)
                if startup or date.today() != today:
                    today, file_path = update_csv(count_num)
                    startup = False
                seq = create_sequence()
                valid, msg = evaluate_sequence(seq, hw)
                if not valid:
                    ui.clear()
                    ui.message("INVALID SEQ", 1)
                    ui.message(msg, 2, 5)
                    exit(1)
                part_num, mach_num, counter_stop_point = read_production_info()
                mode = MODES["standby"]
                production_file_modify_time = get_file_modify_time(PRODUCTION_INFO_FILE)

            elif mode == MODES["standby"]:
                ui.display_standby(part_num, total_count, mach_num, counter_stop_point)
                while mode == MODES["standby"]:
                    if hw.rfid_bypass.is_pressed:
                        ui.message(f"{part_num} BYPASS", 1)
                        time.sleep(0.5)
                    else:
                        reader = hw.init_reader()
                        idn, emp_num = reader.read_no_block()
                        if emp_num:
                            emp_num = emp_num.strip()
                            emp_name = employees.get(emp_num.lower(), None)  # Inline lookup
                            add_timestamp(LOGON, file_path, count_num, mach_num, part_num, emp_num)
                            logon_time = datetime.now()
                            mode = MODES["run"]

                    if hw.button1.is_pressed:
                        ui.message("Hold 3 sec>>Menu", 1)
                        button_press_time = datetime.now()
                        hw.button1.wait_for_release()
                        if datetime.now() >= button_press_time + timedelta(seconds=2.5):
                            mode = MODES["menu"]

                    if mode == MODES["standby"] and hw.button2.is_pressed:
                        ui.message("Hold 3 sec>>Load", 1)
                        button_press_time = datetime.now()
                        hw.button2.wait_for_release()
                        if datetime.now() >= button_press_time + timedelta(seconds=8):
                            write_card(hw, ui)
                            exit_and_reload()
                        elif datetime.now() >= button_press_time + timedelta(seconds=2.5):
                            exit_and_reload()

                    if mode == MODES["standby"] and datetime.now() >= last_load_time + timedelta(
                            seconds=RELOAD_SECONDS):
                        potential_reboot()
                        if get_file_modify_time(PRODUCTION_INFO_FILE) != production_file_modify_time:
                            exit_and_reload()
                        last_load_time = datetime.now()

            elif mode == MODES["menu"]:
                ui.clear()
                ui.message("Reset Counter?", 1)
                ui.message("Gr=Yes Red=No", 2)
                while mode == MODES["menu"]:
                    if hw.button2.is_pressed:
                        hw.button2.wait_for_release()
                        total_count = 0
                        update_total_count(total_count)
                        ui.message("Counter= 0", 1, 3)
                        mode = MODES["standby"]
                    if hw.button1.is_pressed:
                        hw.button1.wait_for_release()
                        mode = MODES["standby"]

            elif mode == MODES["run"]:
                emp_count = 0
                last_shot_run_time = datetime.now()
                ui.clear()
                while mode == MODES["run"]:
                    ui.display_run(emp_name, emp_num, emp_count, total_count, logon_time)

                    # Check for sequence trigger
                    run_shot = False
                    if triggers == 2:
                        if hw.trigger_1.is_pressed and hw.trigger_2.is_pressed:
                            run_shot = True
                    else:
                        if hw.trigger_1.is_pressed:
                            run_shot = True

                    if run_shot and datetime.now() >= last_shot_run_time + timedelta(seconds=1):
                        emp_count += 1
                        total_count += 1
                        update_total_count(total_count)
                        add_timestamp(SHOT, file_path, count_num, mach_num, part_num, emp_num)
                        run_sequence(seq, hw)
                        last_shot_run_time = datetime.now()
                        if triggers == 2:
                            if hw.trigger_2.is_pressed:
                                hw.trigger_2.wait_for_release()
                        else:
                            if hw.trigger_1.is_pressed:
                                hw.trigger_2.wait_for_release()

                    # Count stop check
                    if total_count >= counter_stop_point:
                        add_timestamp(LOGOUT, file_path, count_num, mach_num, part_num, emp_num)
                        total_count = 0
                        update_total_count(total_count)
                        ui.clear()
                        ui.message("Count Reached", 1)
                        ui.message("Press Red Btn", 2)
                        hw.button1.wait_for_press()
                        hw.button1.wait_for_release()
                        mode = MODES["standby"]

                    # Timeout check
                    if datetime.now() >= last_shot_run_time + timedelta(seconds=TIMEOUT_SECONDS):
                        add_timestamp(TIMEOUT, file_path, count_num, mach_num, part_num, emp_num)
                        ui.message("Timed Out", 1, 5)
                        mode = MODES["standby"]

                    # Logout button
                    if hw.button1.is_pressed:
                        hw.button1.wait_for_release()
                        add_timestamp(LOGOUT, file_path, count_num, mach_num, part_num, emp_num)
                        ui.message("Logged Out", 1, 1)
                        mode = MODES["standby"]

    except Exception as e:
        ui.clear()
        ui.message("ERROR", 1)
        print(e)
        time.sleep(5)
    finally:
        hw.close()


if __name__ == "__main__":
    main()