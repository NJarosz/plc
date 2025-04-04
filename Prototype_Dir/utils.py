# rfid_utils.py
import time
from config import WRITER_FILE

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