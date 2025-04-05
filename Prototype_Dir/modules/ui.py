# ui.py
import time
from datetime import datetime, timedelta
from config import DEFAULT_COUNT_STOP

class UI:
    def __init__(self, lcd):
        self.lcd = lcd

    def clear(self):
        """Clear the LCD."""
        self.lcd.clear()

    def message(self, msg, line=1, delay=0):
        """Display a message on the specified line with optional delay."""
        self.lcd.message(msg.ljust(16)[:16], line)
        if delay:
            time.sleep(delay)

    def display_standby(self, part_num, total_count, mach_num, counter_stop_point):
        """Show standby info."""
        self.clear()
        top = f"{part_num}"
        bottom = f"{total_count}"
        if counter_stop_point != DEFAULT_COUNT_STOP:
            bottom += f"/{counter_stop_point}"
        bottom = bottom.ljust(16 - len(mach_num)) + mach_num
        self.lcd.message(top, 1)
        self.lcd.message(bottom, 2)

    def display_run(self, emp_name, emp_num, emp_count, total_count, logon_time):
        """Show run mode info with runtime."""
        top = f"{emp_name or emp_num or 'Unknown'}"
        bottom = f"{emp_count}   {total_count}"
        delta = datetime.now() - logon_time
        delta_str = str(delta)[2:7] if str(delta).startswith("0") else str(delta)[:5]
        self.lcd.message(f"{top[:8]} {delta_str}", 1, 1)
        self.lcd.message(bottom, 2)