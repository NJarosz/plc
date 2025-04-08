from utils import handle_error
from file_io import update_total_count
from config import MODES

def run_menu_mode(ui, hw, state):
    """
    Handle the 'menu' mode: allow counter reset via buttons.
    Returns next mode and updated state.
    """
    ui.clear()
    ui.message("Reset Counter?", 1)
    ui.message("Gr=Yes Red=No", 2)
    while True:
        if hw.button_2.is_pressed:
            hw.button_2.wait_for_release()
            state["total_count"] = 0
            update_total_count(state["total_count"])
            ui.message("Counter= 0", 1, 3)
            return MODES["standby"], state
        if hw.button_1.is_pressed:
            hw.button_1.wait_for_release()
            return MODES["standby"], state
    return MODES["standby"], state  # Fallback, though loop should exit via buttons