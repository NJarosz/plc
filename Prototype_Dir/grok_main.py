import sys
import time
import os
from datetime import datetime, timedelta, date
from hardware import Hardware
from sequence import create_sequence, evaluate_sequence, run_sequence
from file_io import load_employee_list, update_csv, add_timestamp, read_total_count, update_total_count, \
    get_file_modify_time, read_production_info
from ui import UI
from utils import write_card  # Importing from utils.py as requested
from config import *

def potential_reboot(boot_time):
    print("Checking for reboot...")
    timenow = datetime.now()
    if timenow > boot_time + timedelta(seconds=REBOOT_WAIT_SECONDS) and timenow.hour == REBOOT_HOUR:
        print("Reboot condition met. Rebooting...")
        ui.clear()
        ui.message("Rebooting ...", 1)
        os.system("sudo reboot")
    else:
        print("No reboot needed.")

def exit_and_reload():
    print("Exiting and reloading...")
    ui.clear()
    ui.message("Reloading ...", 1)
    sys.exit(0)

def main():
    print("Starting main()...")
    triggers = sys.argv[1].upper().strip() if len(sys.argv) > 1 else "default"
    print(f"Triggers set to: {triggers}")

    try:
        hw = Hardware(triggers)
        print("Hardware initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize hardware: {e}")
        sys.exit(1)

    ui = UI(hw.lcd)
    mode = MODES["load"]
    startup = True
    print("Loading employee list...")
    try:
        employees, employees_loaded = load_employee_list()
        print(f"Employees loaded: {employees_loaded}, Count: {len(employees)}")
    except Exception as e:
        print(f"Error loading employees: {e}")
        employees, employees_loaded = {}, False

    total_count = read_total_count()
    print(f"Initial total_count: {total_count}")
    emp_num, emp_name = None, None
    today, file_path = None, None
    logon_time = None
    boot_time = datetime.now()
    last_load_time = datetime.now()
    print(f"Boot time: {boot_time}")

    try:
        while True:
            print(f"Current mode: {mode}")
            if mode == MODES["load"]:
                print("Entering load mode...")
                ui.clear()
                ui.message("Loading Info...", 1, 5)
                if startup or date.today() != today:
                    print("Updating CSV due to startup or new day...")
                    try:
                        today, file_path = update_csv(count_num)
                        print(f"CSV updated: {file_path}")
                    except Exception as e:
                        print(f"Error updating CSV: {e}")
                        ui.message("CSV ERROR", 1, 5)
                        mode = MODES["error"]
                        continue
                    startup = False
                print("Creating sequence...")
                try:
                    seq = create_sequence()
                    print(f"Sequence created: {seq}")
                    valid, msg = evaluate_sequence(seq, hw)
                    if not valid:
                        print(f"Sequence invalid: {msg}")
                        ui.clear()
                        ui.message("INVALID SEQ", 1)
                        ui.message(msg, 2, 5)
                        mode = MODES["error"]
                        continue
                except Exception as e:
                    print(f"Error creating/evaluating sequence: {e}")
                    ui.message("SEQ ERROR", 1, 5)
                    mode = MODES["error"]
                    continue
                print("Reading production info...")
                try:
                    part_num, mach_num, counter_stop_point = read_production_info()
                    print(f"Production info: {part_num}, {mach_num}, {counter_stop_point}")
                except Exception as e:
                    print(f"Error reading production info: {e}")
                    ui.message("PROD ERROR", 1, 5)
                    mode = MODES["error"]
                    continue
                mode = MODES["standby"]
                production_file_modify_time = get_file_modify_time(PRODUCTION_INFO_FILE)
                print(f"Switched to standby mode. Prod file mod time: {production_file_modify_time}")

            elif mode == MODES["standby"]:
                print("Entering standby mode...")
                try:
                    ui.display_standby(part_num, total_count, mach_num, counter_stop_point)
                    print("Standby display updated.")
                except Exception as e:
                    print(f"Error displaying standby: {e}")
                    ui.clear()
                    ui.message("STANDBY ERROR", 1)
                    ui.message(str(e)[:16], 2, 5)
                    mode = MODES["error"]
                    continue
                while mode == MODES["standby"]:
                    if hw.rfid_bypass.is_pressed:
                        print("RFID bypass pressed.")
                        ui.message(f"{part_num} BYPASS", 1)
                        time.sleep(0.5)
                    else:
                        print("Initializing RFID reader...")
                        try:
                            reader = hw.init_reader()
                            idn, emp_num = reader.read_no_block()
                            if emp_num:
                                emp_num = emp_num.strip()
                                emp_name = employees.get(emp_num.lower(), None)
                                print(f"RFID read: {emp_num}, Name: {emp_name}")
                                add_timestamp(LOGON, file_path, count_num, mach_num, part_num, emp_num)
                                logon_time = datetime.now()
                                mode = MODES["run"]
                                print("Switched to run mode.")
                        except Exception as e:
                            print(f"Error with RFID reader: {e}")
                            mode = MODES["error"]
                            break

                    if hw.button_1.is_pressed:  # Changed from button1
                        print("Button 1 pressed.")
                        ui.message("Hold 3 sec>>Menu", 1)
                        button_press_time = datetime.now()
                        hw.button_1.wait_for_release()
                        if datetime.now() >= button_press_time + timedelta(seconds=2.5):
                            mode = MODES["menu"]
                            print("Switched to menu mode.")

                    if mode == MODES["standby"] and hw.button_2.is_pressed:  # Changed from button2
                        print("Button 2 pressed.")
                        ui.message("Hold 3 sec>>Load", 1)
                        button_press_time = datetime.now()
                        hw.button_2.wait_for_release()
                        if datetime.now() >= button_press_time + timedelta(seconds=8):
                            print("Writing card and reloading...")
                            write_card(hw, ui)
                            exit_and_reload()
                        elif datetime.now() >= button_press_time + timedelta(seconds=2.5):
                            print("Reloading...")
                            exit_and_reload()

                    if mode == MODES["standby"] and datetime.now() >= last_load_time + timedelta(seconds=RELOAD_SECONDS):
                        print("Checking reload conditions...")
                        potential_reboot(boot_time)
                        if get_file_modify_time(PRODUCTION_INFO_FILE) != production_file_modify_time:
                            print("Production file changed. Reloading...")
                            exit_and_reload()
                        last_load_time = datetime.now()

            elif mode == MODES["menu"]:
                print("Entering menu mode...")
                ui.clear()
                ui.message("Reset Counter?", 1)
                ui.message("Gr=Yes Red=No", 2)
                while mode == MODES["menu"]:
                    if hw.button_2.is_pressed:  # Changed from button2
                        print("Button 2 pressed in menu: Resetting counter.")
                        hw.button_2.wait_for_release()
                        total_count = 0
                        update_total_count(total_count)
                        ui.message("Counter= 0", 1, 3)
                        mode = MODES["standby"]
                        print("Switched to standby mode.")
                    if hw.button_1.is_pressed:  # Changed from button1
                        print("Button 1 pressed in menu: No reset.")
                        hw.button_1.wait_for_release()
                        mode = MODES["standby"]
                        print("Switched to standby mode.")

            elif mode == MODES["run"]:
                print("Entering run mode...")
                emp_count = 0
                last_shot_run_time = datetime.now()
                ui.clear()
                while mode == MODES["run"]:
                    try:
                        ui.display_run(emp_name, emp_num, emp_count, total_count, logon_time)
                        print("Run display updated.")
                    except Exception as e:
                        print(f"Error displaying run: {e}")
                        mode = MODES["error"]
                        break

                    run_shot = False
                    if triggers == "2":  # Assuming triggers can be "2" for dual triggers
                        if hw.trigger_1.is_pressed and hw.trigger_2.is_pressed:
                            run_shot = True
                    else:
                        if hw.trigger_1.is_pressed:
                            run_shot = True

                    if run_shot and datetime.now() >= last_shot_run_time + timedelta(seconds=1):
                        print("Running sequence...")
                        emp_count += 1
                        total_count += 1
                        update_total_count(total_count)
                        add_timestamp(SHOT, file_path, count_num, mach_num, part_num, emp_num)
                        try:
                            run_sequence(seq, hw)
                            print("Sequence executed.")
                        except Exception as e:
                            print(f"Error running sequence: {e}")
                            mode = MODES["error"]
                            break
                        last_shot_run_time = datetime.now()
                        if triggers == "2" and hw.trigger_2.is_pressed:
                            hw.trigger_2.wait_for_release()
                        elif hw.trigger_1.is_pressed:
                            hw.trigger_1.wait_for_release()

                    if total_count >= counter_stop_point:
                        print("Counter stop point reached.")
                        add_timestamp(LOGOUT, file_path, count_num, mach_num, part_num, emp_num)
                        total_count = 0
                        update_total_count(total_count)
                        ui.clear()
                        ui.message("Count Reached", 1)
                        ui.message("Press Red Btn", 2)
                        hw.button_1.wait_for_press()
                        hw.button_1.wait_for_release()
                        mode = MODES["standby"]
                        print("Switched to standby mode.")

                    if datetime.now() >= last_shot_run_time + timedelta(seconds=TIMEOUT_SECONDS):
                        print("Timeout occurred.")
                        add_timestamp(TIMEOUT, file_path, count_num, mach_num, part_num, emp_num)
                        ui.message("Timed Out", 1, 5)
                        mode = MODES["standby"]
                        print("Switched to standby mode.")

                    if hw.button_1.is_pressed:  # Changed from button1
                        print("Button 1 pressed in run: Logging out.")
                        hw.button_1.wait_for_release()
                        add_timestamp(LOGOUT, file_path, count_num, mach_num, part_num, emp_num)
                        ui.message("Logged Out", 1, 1)
                        mode = MODES["standby"]
                        print("Switched to standby mode.")

            elif mode == MODES["error"]:
                print("Entering error mode...")
                ui.clear()
                ui.message("ERROR STATE", 1)
                ui.message("Restarting...", 2, 5)
                hw.close()
                sys.exit(1)

    except KeyboardInterrupt:
        print("Program interrupted by user.")
        hw.close()
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error in main loop: {e}")
        ui.clear()
        ui.message("FATAL ERROR", 1)
        ui.message(str(e)[:16], 2, 5)
        hw.close()
        sys.exit(1)
    finally:
        print("Cleaning up hardware...")
        hw.close()

if __name__ == "__main__":
    main()