# file_io.py
import csv
import os
import time
from datetime import date
from config import *

def get_file_modify_time(filename):
    """Return the modification time of a file, or -1 if not found."""
    try:
        return os.path.getmtime(filename)
    except:
        return -1

def load_employee_list(filename=EMPLOYEE_INFO_FILE):
    """Load employee ID-to-name mapping."""
    emps = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.strip() and "#" not in line:
                    key, value = line.replace(' ', '').strip().split(",")
                    emps[key.lower()] = value
        return emps, True
    except:
        return {}, False

def read_production_info(filename=PRODUCTION_INFO_FILE):
    """Read part, machine, and count stop from file."""
    part, machine, count_stop = DEFAULT_PART_NUMBER, DEFAULT_MACHINE, DEFAULT_COUNT_STOP
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.strip() and "#" not in line:
                    key, value = line.replace(' ', '').strip().split(",")
                    key = key.lower()
                    if key == "part":
                        part = value.upper()
                    elif key == "machine":
                        machine = value.upper()
                    elif key == "count_stop":
                        count_stop = int(value) if value.isdigit() else count_stop
    except:
        pass
    part = part.strip()[:MAX_PART_NUMBER_LENGTH]
    machine = machine.strip()[:MAX_MACHINE_LENGTH]
    if not (MIN_COUNT_STOP <= count_stop <= DEFAULT_COUNT_STOP):
        count_stop = DEFAULT_COUNT_STOP
    return part, machine, count_stop

def update_csv(pi_num):
    """Create or update daily CSV file."""
    today = date.today()
    file_path = f"{CSV_PATH}{today.strftime('%Y%m%d')}{pi_num}.csv"
    if not os.path.exists(file_path):
        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "pi", "Machine", "Part", "User_ID", "Time", "Date"])
    return today, file_path

def add_timestamp(event, file_path, pi_num, mach_num, part_num, emp_num):
    """Log an event to CSV."""
    now = time.strftime("%H:%M:%S")
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([event, pi_num, mach_num, part_num, emp_num, now, date.today()])

def read_total_count():
    """Read total count from file."""
    try:
        with open(TOTALCOUNT_FILE, "r") as f:
            cnt = int(f.readline().strip())
            return max(0, min(cnt, DEFAULT_COUNT_STOP))
    except:
        return 0

def update_total_count(total_count):
    """Write total count to file."""
    try:
        with open(TOTALCOUNT_FILE, "w") as f:
            f.write(str(total_count))
        return os.path.getmtime(TOTALCOUNT_FILE)
    except:
        return -1