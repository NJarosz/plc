import sys
import time
import os
from datetime import datetime, timedelta, date
from Prototype_Dir.modules.hardware import Hardware
from Prototype_Dir.modules.sequence import create_sequence, evaluate_sequence, run_sequence
from Prototype_Dir.modules.file_io import load_employee_list, update_csv, add_timestamp, read_total_count, update_total_count, \
    get_file_modify_time, read_production_info
from Prototype_Dir.modules.ui import UI
from Prototype_Dir.modules.utils import write_card, potential_reboot, exit_and_reload, handle_error
from config import *

def main():
    triggers = sys.argv[1].upper().strip() if len(sys.argv) > 1 else DEFAULT_TRIGGERS
    #print(f"Triggers set to: {triggers}")
    try:
        hw = Hardware(triggers)
        ui = UI(hw.lcd)
        #print("Hardware and UI initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize hardware/UI: {e}")
        sys.exit(1)

    mode = MODES["load"]
    startup = True
    employees, employees_loaded = load_employee_list() or ({}, False)           # try/except in function returns ({}, False)- redundant
    #print(f"Employees loaded: {employees_loaded}, Count: {len(employees)}")
    total_count = read_total_count()
    #print(f"Initial total_count: {total_count}")
    emp_num, emp_name = None, None
    today, file_path = None, None
    logon_time = None
    boot_time = datetime.now()
    last_load_time = boot_time
    seq, part_num, mach_num, counter_stop_point = None, None, None, None
    production_file_modify_time = None
    #print(f"Boot time: {boot_time}")

    try:
        while True:
            #print(f"Current mode: {mode}")
            if mode == MODES["load"]:
                #print("Entering load mode...")
                ui.clear()
                ui.message("Loading Info...", 1, 5)
                if startup or date.today() != today:
                    #print("Updating CSV due to startup or new day...")
                    try:
                        today, file_path = update_csv(PI_NUM)
                        #print(f"CSV updated: {file_path}")
                    except Exception as e:
                        mode = handle_error(ui, "CSV ERROR", e)
                        continue
                    startup = False
                #print("Creating sequence...")
                try:
                    seq = create_sequence()
                    #print(f"Sequence created: {seq}")
                    valid, msg = evaluate_sequence(seq, hw)
                    if not valid:
                        mode = handle_error(ui, "INVALID SEQ", msg)
                        continue
                    part_num, mach_num, counter_stop_point = read_production_info()
                    #print(f"Production info: {part_num}, {mach_num}, {counter_stop_point}")
                except Exception as e:
                    mode = handle_error(ui, "LOAD ERROR", e)
                    continue
                mode = MODES["standby"]
                production_file_modify_time = get_file_modify_time(PRODUCTION_INFO_FILE)
                #print(f"Switched to standby mode. Prod file mod time: {production_file_modify_time}")

            elif mode == MODES["standby"]:
                #print("Entering standby mode...")
                try:
                    ui.display_standby(part_num, total_count, mach_num, counter_stop_point)
                    #print("Standby display updated.")
                except Exception as e:
                    mode = handle_error(ui, "STANDBY ERROR", e)
                    continue
                while mode == MODES["standby"]:
                    if hw.rfid_bypass.is_pressed:
                        #print("RFID bypass pressed.")
                        ui.message(f"{part_num} BYPASS", 1)
                        time.sleep(0.5)
                    else:
                        #print("Initializing RFID reader...")
                        try:
                            reader = hw.init_reader()
                            idn, emp_num = reader.read_no_block()
                            if emp_num:
                                emp_num = emp_num.strip()
                                emp_name = employees.get(emp_num.lower(), None)
                                #print(f"RFID read: {emp_num}, Name: {emp_name}")
                                add_timestamp(LOGON, file_path, PI_NUM, mach_num, part_num, emp_num)
                                logon_time = datetime.now()
                                mode = MODES["run"]
                                #print("Switched to run mode.")
                        except Exception as e:
                            mode = handle_error(ui, "RFID ERROR", e)
                            break

                    if hw.button_1.is_pressed:
                        #print("Button 1 pressed.")
                        ui.message("Hold 3 sec>>Menu", 1)
                        button_press_time = datetime.now()
                        hw.button_1.wait_for_release()
                        if datetime.now() >= button_press_time + timedelta(seconds=MENU_BUTTON_HOLD_SECONDS):
                            mode = MODES["menu"]
                            #print("Switched to menu mode.")

                    if mode == MODES["standby"] and hw.button_2.is_pressed:
                        #print("Button 2 pressed.")
                        ui.message("Hold 3 sec>>Load", 1)
                        button_press_time = datetime.now()
                        hw.button_2.wait_for_release()
                        if datetime.now() >= button_press_time + timedelta(seconds=CARD_WRITE_HOLD_SECONDS):
                            #print("Writing card and reloading...")
                            write_card(hw, ui)
                            exit_and_reload(ui)
                        elif datetime.now() >= button_press_time + timedelta(seconds=LOAD_BUTTON_HOLD_SECONDS):
                            #print("Reloading...")
                            exit_and_reload(ui)

                    if mode == MODES["standby"] and datetime.now() >= last_load_time + timedelta(seconds=RELOAD_SECONDS):
                        #print("Checking reload conditions...")
                        potential_reboot(boot_time, ui)
                        if get_file_modify_time(PRODUCTION_INFO_FILE) != production_file_modify_time:
                            #print("Production file changed. Reloading...")
                            exit_and_reload(ui)
                        last_load_time = datetime.now()

            elif mode == MODES["menu"]:
                #print("Entering menu mode...")
                ui.clear()
                ui.message("Reset Counter?", 1)
                ui.message("Gr=Yes Red=No", 2)
                while mode == MODES["menu"]:
                    if hw.button_2.is_pressed:
                        #print("Button 2 pressed in menu: Resetting counter.")
                        hw.button_2.wait_for_release()
                        total_count = 0
                        update_total_count(total_count)
                        ui.message("Counter= 0", 1, 3)
                        mode = MODES["standby"]
                        #print("Switched to standby mode.")
                    if hw.button_1.is_pressed:
                        #print("Button 1 pressed in menu: No reset.")
                        hw.button_1.wait_for_release()
                        mode = MODES["standby"]
                        #print("Switched to standby mode.")

            elif mode == MODES["run"]:
                #print("Entering run mode...")
                emp_count = 0
                last_shot_run_time = datetime.now()
                ui.clear()
                while mode == MODES["run"]:
                    try:
                        ui.display_run(emp_name, emp_num, emp_count, total_count, logon_time)
                        #print("Run display updated.")
                    except Exception as e:
                        mode = handle_error(ui, "RUN ERROR", e)
                        break

                    run_shot = triggers == "2" and hw.trigger_1.is_pressed and hw.trigger_2.is_pressed or \
                              hw.trigger_1.is_pressed
                    if run_shot and datetime.now() >= last_shot_run_time + timedelta(seconds=SEQUENCE_DEBOUNCE_SECONDS):
                        #print("Running sequence...")
                        emp_count += 1
                        total_count += 1
                        update_total_count(total_count)
                        add_timestamp(SHOT, file_path, PI_NUM, mach_num, part_num, emp_num)
                        try:
                            run_sequence(seq, hw)
                            #print("Sequence executed.")
                        except Exception as e:
                            mode = handle_error(ui, "SEQ ERROR", e)
                            break
                        last_shot_run_time = datetime.now()
                        if triggers == "2" and hw.trigger_2.is_pressed:
                            hw.trigger_2.wait_for_release()
                        elif hw.trigger_1.is_pressed:
                            hw.trigger_1.wait_for_release()

                    if total_count >= counter_stop_point:
                        #print("Counter stop point reached.")
                        add_timestamp(LOGOUT, file_path, PI_NUM, mach_num, part_num, emp_num)
                        total_count = 0
                        update_total_count(total_count)
                        ui.clear()
                        ui.message("Count Reached", 1)
                        ui.message("Press Red Btn", 2)
                        hw.button_1.wait_for_press()
                        hw.button_1.wait_for_release()
                        mode = MODES["standby"]
                        #print("Switched to standby mode.")

                    if datetime.now() >= last_shot_run_time + timedelta(seconds=TIMEOUT_SECONDS):
                        #print("Timeout occurred.")
                        add_timestamp(TIMEOUT, file_path, PI_NUM, mach_num, part_num, emp_num)
                        ui.message("Timed Out", 1, 5)
                        mode = MODES["standby"]
                        #print("Switched to standby mode.")

                    if hw.button_1.is_pressed:
                        #print("Button 1 pressed in run: Logging out.")
                        hw.button_1.wait_for_release()
                        add_timestamp(LOGOUT, file_path, PI_NUM, mach_num, part_num, emp_num)
                        ui.message("Logged Out", 1, 1)
                        mode = MODES["standby"]
                        #print("Switched to standby mode.")

            elif mode == MODES["error"]:
                #print("Entering error mode...")
                hw.close()
                sys.exit(1)

    except KeyboardInterrupt:
        print("Program interrupted by user.")
        hw.close()
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        ui.clear()
        ui.message("FATAL ERROR", 1)
        ui.message(str(e)[:16], 2, 5)
        hw.close()
        sys.exit(1)
    finally:
        #print("Cleaning up hardware...")
        hw.close()

if __name__ == "__main__":
    main()