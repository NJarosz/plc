from modules.file_io import update_csv, read_production_info, get_file_modify_time
from modules.sequence import create_sequence, evaluate_sequence
from modules.utils import handle_error
from config import MODES, PI_NUM, PRODUCTION_INFO_FILE
import logging

logger = logging.getLogger(__name__)

def run_load_mode(ui, hw, state):
    """
    Handle the 'load' mode: initialize CSV, sequence, and production info.
    Returns next mode and updated state.
    """
    ui.clear()
    ui.message("Loading Info...", 1, 5)
    logger.info("Loading Info...")
    if state["startup"] or date.today() != state["today"]:
        try:
            state["today"], state["file_path"] = update_csv(PI_NUM)
        except Exception as e:
            return handle_error(ui, "CSV ERROR", e), state
        state["startup"] = False
    try:
        state["seq"] = create_sequence()
        valid, msg = evaluate_sequence(state["seq"], hw)
        if not valid:
            return handle_error(ui, "INVALID SEQ", msg), state
        state["part_num"], state["mach_num"], state["counter_stop_point"] = read_production_info()
        logger.info(f"Information loaded: {state['file_path']}, {state['part_num']}, {state['mach_num']}, {state['counter_stop_point']}")
        logger.info(f"Sequence loaded: {state['seq']}, {valid}")
    except Exception as e:
        return handle_error(ui, "LOAD ERROR", e), state
    state["production_file_modify_time"] = get_file_modify_time(PRODUCTION_INFO_FILE)
    return MODES["standby"], state