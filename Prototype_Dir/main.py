import sys
import logging
from datetime import datetime
from modules.hardware import Hardware
from modules.ui import UI
from modules.file_io import load_employee_list, read_total_count
from modes.load_mode import run_load_mode
from modes.standby_mode import run_standby_mode
from modes.menu_mode import run_menu_mode
from modes.run_mode import run_run_mode
from modes.error_mode import run_error_mode
from config import DEFAULT_TRIGGERS, MODES

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    triggers = sys.argv[1].upper().strip() if len(sys.argv) > 1 else DEFAULT_TRIGGERS  # Sets num of triggers
    try:
        hw = Hardware(triggers)
        ui = UI(hw.lcd)
    except Exception as e:
        print(f"Failed to initialize hardware/UI: {e}")
        sys.exit(1)

    state = {
        "startup": True,
        "employees": load_employee_list()[0],
        "total_count": read_total_count(),
        "emp_num": None,
        "emp_name": None,
        "today": None,
        "file_path": None,
        "logon_time": None,
        "boot_time": datetime.now(),
        "last_load_time": datetime.now(),
        "seq": None,
        "part_num": None,
        "mach_num": None,
        "counter_stop_point": None,
        "production_file_modify_time": None
    }
    mode = MODES["load"]

    try:
        while True:
            if mode == MODES["load"]:
                mode, state = run_load_mode(ui, hw, state)
            elif mode == MODES["standby"]:
                mode, state = run_standby_mode(ui, hw, state, triggers)
            elif mode == MODES["menu"]:
                mode, state = run_menu_mode(ui, hw, state)
            elif mode == MODES["run"]:
                mode, state = run_run_mode(ui, hw, state, triggers)
            elif mode == MODES["error"]:
                mode, state = run_error_mode(ui, hw, state)
                if mode == MODES["error"]:  # Exit on error mode persistence
                    break
    except KeyboardInterrupt:
        print("Program interrupted by user.")
        hw.close()
        sys.exit(0)
    finally:
        hw.close()

if __name__ == "__main__":
    main()