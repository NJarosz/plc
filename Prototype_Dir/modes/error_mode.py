from config import MODES

def run_error_mode(ui, hw, state):
    """
    Handle the 'error' mode: display error state and exit.
    Returns next mode and updated state (though typically exits).
    """
    ui.clear()
    ui.message("ERROR STATE", 1)
    ui.message("Restarting...", 2, 5)
    hw.close()
    return MODES["error"], state  # Signals main loop to exit