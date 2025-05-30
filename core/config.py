# config.py
# Constants and settings for the PLC

# PLC Number
with open("/etc/hostname", "r") as hn:
    pi = hn.readline().rstrip("\n")
PI_NUM = int(''.join(i for i in pi if i.isdigit()))

# File paths
EMPLOYEE_INFO_FILE = "../data/employees.json"
PRODUCTION_INFO_FILE = "../data/production.json"
TOTALCOUNT_FILE = "../data/totalcount.json"
WRITER_FILE = "../docs/writer.txt"
PROGRAM_FOLDER = "../scripts/plc_programs/"
MAIN_PROGRAM_NAME = PROGRAM_FOLDER + "main.plc"
CSV_PATH = "../data/csv/"

# Button hold times
MENU_BUTTON_HOLD_SECONDS = 2.6  # Needs to be a number
LOAD_BUTTON_HOLD_SECONDS = 2.6  # Needs to be a number
CARD_WRITE_HOLD_SECONDS = 8.0   # Needs to be a number

# Sequence debounce time
SEQUENCE_DEBOUNCE_SECONDS = 1.0

# Default triggers
DEFAULT_TRIGGERS = "default"

# GPIO pin assignments (Pi Zero W)
RELAY_PINS = [4, 17, 27, 22, 5, 6, 13, 19]  # 8 relays,
BUTTON_PINS = {
    "red": 12,        # Pin 32
    "green": 16,      # Pin 36
    "bypass": 26,     # Pin 37
    "trigger_1": 20,  # Pin 38
    "trigger_2": 21   # Pin 40
}
# I2C (LCD): GPIO 2, 3 (pins 3, 5) - fixed in hardware
# SPI (RFID): GPIO 7, 9, 10, 11, 25 (pins 24, 21, 19, 23, 22) - fixed in hardware

# General settings
MAX_DISPLAY_LEN = 16
TIMEOUT_SECONDS = 300
DEFAULT_PART_NUMBER = "99999"
MAX_PART_NUMBER_LENGTH = 12
DEFAULT_MACHINE = "UNK"
MAX_MACHINE_LENGTH = 5
DEFAULT_COUNT_STOP = 999999
MIN_COUNT_STOP = 0
REBOOT_HOUR = 4
REBOOT_WAIT_SECONDS = 14800
RELOAD_SECONDS = 30

# Modes
MODES = {
    "setup": 0,
    "standby": 1,
    "menu": 2,
    "run": 3,
    "load": 4,
    "error": 5
}

# Event types
LOGON = "LOG_ON"
LOGOUT = "LOG_OFF"
TIMEOUT = "TIME_OUT"
SHOT = "SHOT"
