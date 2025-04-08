import time
from datetime import datetime, timedelta
from sequence import run_sequence
from file_io import add_timestamp, update_total_count
from utils import handle_error
from config import MODES, PI_NUM, SEQUENCE_DEBOUNCE_SECONDS, TIMEOUT_SECONDS

def run_run_mode(ui, hw, state, triggers):
    """
    Handle the 'run' mode: execute sequences based on triggers, manage counters and timeouts.
    Returns next mode and updated state.
    """
    emp_count = 0
    last_shot_run_time = datetime.now()
    ui.clear()
    while True:
        try:
            ui.display_run(state["emp_name"], state["emp_num"], emp_count, state["total_count"], state["logon_time"])
        except Exception as e:
            return handle_error(ui, "RUN ERROR", e), state

        run_shot = (triggers == "2" and hw.trigger_1.is_pressed and hw.trigger_2.is_pressed) or \
                   hw.trigger_1.is_pressed
        if run_shot and datetime.now() >= last_shot_run_time + timedelta(seconds=SEQUENCE_DEBOUNCE_SECONDS):
            emp_count += 1
            state["total_count"] += 1
            update_total_count(state["total_count"])
            add_timestamp("SHOT", state["file_path"], PI_NUM, state["mach_num"], state["part_num"], state["emp_num"])
            try:
                run_sequence(state["seq"], hw)
            except Exception as e:
                return handle_error(ui, "SEQ ERROR", e), state
            last_shot_run_time = datetime.now()
            if hw.trigger_1.is_pressed:
                hw.trigger_1.wait_for_release()
            if triggers == "2" and hw.trigger_2.is_pressed:
                hw.trigger_2.wait_for_release()


        if state["total_count"] >= state["counter_stop_point"]:
            add_timestamp("LOG_OFF", state["file_path"], PI_NUM, state["mach_num"], state["part_num"], state["emp_num"])
            state["total_count"] = 0
            update_total_count(state["total_count"])
            ui.clear()
            ui.message("Count Reached", 1)
            ui.message("Press Red Btn", 2)
            hw.button_1.wait_for_press()
            hw.button_1.wait_for_release()
            return MODES["standby"], state

        if datetime.now() >= last_shot_run_time + timedelta(seconds=TIMEOUT_SECONDS):
            add_timestamp("TIME_OUT", state["file_path"], PI_NUM, state["mach_num"], state["part_num"], state["emp_num"])
            ui.message("Timed Out", 1, 5)
            return MODES["standby"], state

        if hw.button_1.is_pressed:
            hw.button_1.wait_for_release()
            add_timestamp("LOG_OFF", state["file_path"], PI_NUM, state["mach_num"], state["part_num"], state["emp_num"])
            ui.message("Logged Out", 1, 1)
            return MODES["standby"], state

    return MODES["standby"], state  # Fallback, though loop typically exits via conditions