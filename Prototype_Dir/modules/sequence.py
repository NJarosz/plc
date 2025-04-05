# sequence.py
import time
from Prototype_Dir.modules.hardware import Hardware
from config import MAIN_PROGRAM_NAME, PROGRAM_FOLDER

def read_main():
    """Read the sequence file name from the main program file."""
    try:
        with open(MAIN_PROGRAM_NAME, 'r') as m:
            return m.readline().rstrip("\n").strip()
    except:
        return None

def create_sequence(filename=None):
    """Parse relay sequence from a text file. If no filename provided, use read_main()."""
    if filename is None:
        filename = read_main()
        if filename is None:
            return {}
        filename = PROGRAM_FOLDER + filename

    sequence = {}
    ind = 1
    try:
        with open(filename, 'r') as text:
            for line in text:
                if line.strip() and "#" not in line:
                    key, value = line.replace(' ', '').strip().split(",")
                    key = key.lower()
                    if key == "tmr":
                        sequence[f"{ind}-tmr"] = float(value) / 1000
                        ind += 1
                    elif key in ("on", "off"):
                        sequence[f"{ind}-{key}"] = int(value)  # Relay number (1-8)
                        ind += 1
                    else:
                        return {}
    except:
        return {}
    return sequence

def evaluate_sequence(seq_dict, hw):
    """Validate sequence for errors."""
    relay_state = [False] * len(hw.relays)
    for key, value in seq_dict.items():
        if "on" in key or "off" in key:
            relay_idx = value - 1
            if not (0 <= relay_idx < len(hw.relays)):
                return False, f"Invalid Relay #{value}"
            if "on" in key:
                if relay_state[relay_idx]:
                    return False, f"# {value} already on"
                relay_state[relay_idx] = True
            elif "off" in key:
                if not relay_state[relay_idx]:
                    return False, f"# {value} already off"
                relay_state[relay_idx] = False
        elif "tmr" in key:
            if not isinstance(value, float) or value >= 5:
                return False, "Invalid Timer"
    if not seq_dict:
        return False, "Empty File"
    if any(relay_state):
        return False, f"Relay {relay_state.index(True) + 1} left on"
    return True, "Valid"

def run_sequence(seq_dict, hw):
    """Execute the relay sequence."""
    try:
        for key, value in seq_dict.items():
            if "on" in key:
                hw.relays[value - 1].on()
            elif "off" in key:
                hw.relays[value - 1].off()
            elif "tmr" in key:
                time.sleep(value)
        hw.cleanup()
    except:
        hw.cleanup()
        raise