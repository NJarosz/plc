# rfid_utils.py
import os
import sys
import time
import logging
from datetime import timedelta, datetime
from config import WRITER_FILE, REBOOT_WAIT_SECONDS, REBOOT_HOUR, MODES

logger = logging.getLogger(__name__)

def write_card(hw, ui):
    """Write a string from WRITER_FILE to an RFID card using Hardware and UI instances."""
    ui.clear()
    ui.message("Begin Writing", 1, 3)
    write_str = ''
    try:
        with open(WRITER_FILE, "r") as writefile:
            write_str = writefile.readline().rstrip("\n").strip()
    except:
        amsg = "File Open Error"
    ui.clear()
    if write_str:
        ui.message(write_str, 1)
        ui.message("B=Write R=Skip", 2)
        but_pressed = ''
        while not but_pressed:
            if hw.button1.is_pressed:
                but_pressed = 'R'
            if hw.button2.is_pressed:
                but_pressed = 'B'
        if but_pressed == "R":
            ui.clear()
            ui.message("Write Cancelled", 1, 5)
        else:
            ui.message("Enter Card", 2)
            hw.reader.write(write_str)
            ui.message("Card Written", 2, 5)
    else:
        ui.message("Error Writing", 1)
        ui.message(amsg, 2, 5)


def potential_reboot(boot_time, ui):
    """Check if time has elapsed for a system reboot"""
    #print("Checking for reboot...")
    timenow = datetime.now()
    if timenow > boot_time + timedelta(seconds=REBOOT_WAIT_SECONDS) and timenow.hour == REBOOT_HOUR:
        #print("Reboot condition met. Rebooting...")
        ui.clear()
        ui.message("Rebooting ...", 1)
        os.system("sudo reboot")
    #else:
        #print("No reboot needed.")


def exit_and_reload(ui):
    """Exits and reenters the script"""
    #print("Exiting and reloading...")
    ui.clear()
    ui.message("Reloading ...", 1)
    sys.exit(0)


def handle_error(ui, message, error, delay=8):
    #print(f"Handling error: {message} - {error}")
    ui.clear()
    ui.message(message, 1)
    ui.message(str(error)[:16], 2, delay)
    from config import MODES
    return MODES["error"]