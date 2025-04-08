import time
from datetime import datetime, timedelta
from modules.file_io import add_timestamp, get_file_modify_time
from modules.utils import potential_reboot, exit_and_reload, handle_error
from config import MODES, MENU_BUTTON_HOLD_SECONDS, LOAD_BUTTON_HOLD_SECONDS, CARD_WRITE_HOLD_SECONDS, \
    RELOAD_SECONDS, PRODUCTION_INFO_FILE, PI_NUM
import logging

logger = logging.getLogger(__name__)

def run_standby_mode(ui, hw, state, triggers):
    """
    Handle the 'standby' mode: wait for RFID, button presses, or reload conditions.
    Returns next mode and updated state.
    """
    try:
        ui.display_standby(state["part_num"], state["total_count"], state["mach_num"], state["counter_stop_point"])
    except Exception as e:
        return handle_error(ui, "STANDBY ERROR", e), state

    while True:
        if hw.rfid_bypass.is_pressed:
            ui.message(f"{state['part_num']} BYPASS", 1)
            time.sleep(0.5)
            return MODES["run"], state
        else:
            try:
                reader = hw.init_reader()
                idn, emp_num = reader.read_no_block()
                if emp_num:
                    emp_num = emp_num.strip()
                    state["emp_num"] = emp_num
                    state["emp_name"] = state["employees"].get(emp_num.lower(), None)
                    add_timestamp("LOG_ON", state["file_path"], PI_NUM, state["mach_num"], state["part_num"], emp_num)
                    state["logon_time"] = datetime.now()
                    logger.info(f"LOG-ON: {emp_num}")
                    return MODES["run"], state
            except Exception as e:
                return handle_error(ui, "RFID ERROR", e), state

        if hw.button_1.is_pressed:
            ui.message(f"Hold {round(MENU_BUTTON_HOLD_SECONDS)} sec>>Menu", 1)
            button_press_time = datetime.now()
            hw.button_1.wait_for_release()
            if datetime.now() >= button_press_time + timedelta(seconds=MENU_BUTTON_HOLD_SECONDS):
                return MODES["menu"], state
            else:
                try:
                    ui.display_standby(state["part_num"], state["total_count"], state["mach_num"],
                                       state["counter_stop_point"])
                except Exception as e:
                    return handle_error(ui, "STANDBY ERROR", e), state


        if hw.button_2.is_pressed:
            ui.message(f"Hold {round(LOAD_BUTTON_HOLD_SECONDS)} sec>>Load", 1)
            button_press_time = datetime.now()
            hw.button_2.wait_for_release()
            if datetime.now() >= button_press_time + timedelta(seconds=CARD_WRITE_HOLD_SECONDS):
                write_card(hw, ui)
                exit_and_reload(ui)
            elif datetime.now() >= button_press_time + timedelta(seconds=LOAD_BUTTON_HOLD_SECONDS):
                exit_and_reload(ui)
            else:
                try:
                    ui.display_standby(state["part_num"], state["total_count"], state["mach_num"],
                                       state["counter_stop_point"])
                except Exception as e:
                    return handle_error(ui, "STANDBY ERROR", e), state

        if datetime.now() >= state["last_load_time"] + timedelta(seconds=RELOAD_SECONDS):
            potential_reboot(state["boot_time"], ui)
            if get_file_modify_time(PRODUCTION_INFO_FILE) != state["production_file_modify_time"]:
                exit_and_reload(ui)
            state["last_load_time"] = datetime.now()

        #time.sleep(0.1)
        # If no action, stay in standby (loop continues)
        #return MODES["standby"], state