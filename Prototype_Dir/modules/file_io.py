# file_io.py
import csv
import os
import time
import logging
from datetime import date
from config import *

logger = logging.getLogger(__name__)


def get_file_modify_time(filename):
    """Return the modification time of a file, or -1 if not found."""
    try:
        return os.path.getmtime(filename)
    except OSError as e:
        logger.error(f"Failed to get mod time of {filename}: {e}")
        return -1


def load_employee_list(filename=EMPLOYEE_INFO_FILE):
    try:
        with open(filename, 'r') as f:
            emps = json.load(f)
        logger.debug(f"Loaded employees: {len(emps)} entries")
        return emps, True
    except FileNotFoundError:
        logger.warning(f"Employee file not found: {filename}, using empty dict")
        return {}, True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filename}: {e}")
        return {}, False
    except OSError as e:
        logger.error(f"Failed to read {filename}: {e}")
        return {}, False


def read_production_info(filename=PRODUCTION_INFO_FILE):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data["part"], data["mach"], int(data["count_goal"])
    except (FileNotFoundError, KeyError, ValueError) as e:
        logger.warning(f"Production file issue: {e}, using defaults")
        return "000000", "nA", 0
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filename}: {e}")
        return "000000", "nA", 0
    except OSError as e:
        logger.error(f"Failed to read {filename}: {e}")
        return "000000", "nA", 0


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


def read_total_count(filename=TOTALCOUNT_FILE):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return int(data["count"])
    except (FileNotFoundError, KeyError, ValueError):
        logger.warning(f"Total count file missing or invalid, defaulting to 0")
        return 0
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filename}: {e}")
        return 0
    except OSError as e:
        logger.error(f"Failed to read {filename}: {e}")
        return 0


def update_total_count(count, filename=TOTALCOUNT_FILE):
    try:
        with open(filename, 'w') as f:
            json.dump({"count": count}, f)
        logger.debug(f"Updated total count to {count}")
    except OSError as e:
        logger.error(f"Failed to write total count: {e}")








