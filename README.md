# PLC Control System
A Raspberry Pi-based Programmable Logic Controller (PLC) for managing industrial machine operations. Features include RFID-based employee authentication, shot counting, JSON configuration, automated logging, and a command-line interface (CLI) for configuration.
Features

RFID Authentication: Restricts operation to authorized employees listed in data/employees.json.
State Machine: Manages modes (load, standby, run, menu, error) for robust control.
JSON Configuration: Stores settings in data/production.json and data/total_count.json.
Logging: Records events to logs/plc.log with daily rotation.
CLI Tool: Edit configurations via cli/plc_config.py.
Systemd Integration: Runs as a service (plc.service) with auto-restart.
Modular Design: Organized codebase with separate modules for hardware, file I/O, and UI.


## Directory Structure
```plaintext
plc/
├── core/                    # Main application code
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration variables
│   ├── modules/             # Utility modules
│   │   ├── __init__.py
│   │   ├── file_io.py
│   │   ├── hardware.py
│   │   ├── sequence.py
│   │   ├── ui.py
│   │   ├── utils.py
│   ├── modes/               # State machine modes
│   │   ├── __init__.py
│   │   ├── load_mode.py
│   │   ├── standby_mode.py
│   │   ├── run_mode.py
│   │   ├── menu_mode.py
│   │   ├── error_mode.py
│   ├── lib/                 # External libraries
│   │   ├── __init__.py
│   │   ├── I2C_LCD_driver.py
├── data/                    # Configuration and data files
│   ├── employees.json       # Employee list (ignored by Git)
│   ├── employees.json.template  # Template for employee list
│   ├── production.json      # Production settings (part, machine, count goal)
│   ├── total_count.json     # Total shot count
│   ├── csv/                 # Timestamped CSV logs
│   │   ├── .gitkeep
├── logs/                    # Log files
│   ├── plc.log              # Active log (ignored by Git)
│   ├── plc_YYYYMMDD.log     # Rotated logs (ignored by Git)
│   ├── .gitkeep
├── interface/                     # Command-line tools
│   ├── __init__.py
│   ├── plc_config.py        # CLI for editing JSON configs
│   ├── gui.py               # GUI for updating sequences/ production variables
├── scripts/                 # Automation scripts
│   ├── rotate_plc_logs.sh   # Daily log rotation
│   ├── text_to_json.py      # Converts Text Files to Json
│   ├── plc_programs/        # Files for plc sequences
│   │   ├── main.plc         # Main plc sequence file
│   │   ├── .gitkeep
├── .gitignore               # Excludes sensitive/transient files
├── __init__.py              # Makes plc/ a Python package
├── README.md                # Project documentation
```
## Prerequisites

Hardware: Raspberry Pi (e.g., pi Zero w) with Raspbian, LCD display, RC522 RFID reader, GPIO-connected relays/buttons.
Software:
Python 3.7+
Dependencies: pip3 install gpiozero python3-mfrc522
Systemd for service management



## Setup

Clone the Repository:
git clone https://github.com/yourusername/plc.git
cd plc


## Install Dependencies:
sudo pip3 install gpiozero python3-mfrc522

## Set Up Systemd Service:
sudo nano /etc/systemd/system/plc.service

### Add:
[Unit]
Description=PLC Control Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/plc/core/main.py
WorkingDirectory=/home/pi/plc/core
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=1
User=pi

[Install]
WantedBy=multi-user.target

## Enable and start:
sudo systemctl daemon-reload
sudo systemctl enable plc.service
sudo systemctl start plc.service


## Set Up Log Rotation:
chmod +x scripts/rotate_plc_logs.sh
crontab -e

### Add:
59 23 * * * /home/pi/plc/scripts/rotate_plc_logs.sh


## Set Up Aliases (optional):
nano ~/.bashrc

### Add:
alias plcstatus='sudo systemctl status plc.service'
alias plcstart='sudo systemctl start plc.service'
alias plcstop='sudo systemctl stop plc.service'
alias plcrestart='sudo systemctl restart plc.service'
alias plclogs='journalctl -u plc.service -f'
alias rotatelogs='/home/pi/plc/scripts/rotate_plc_logs.sh'
alias plcconfig='cd /home/pi/plc && python3 -m interface.json_config'

### Apply:
source ~/.bashrc

## Configure JSON Files:

Copy the employee template:cp data/employees.json.template data/employees.json

~$ plcconfig

Edit data/employees.json (e.g., {"123": "John"}).
Verify data/production.json (e.g., {"part": "ABC123", "mach": "M1", "count_goal": 10}).
Verify data/total_count.json (e.g., {"count": 0}).


# Usage

Start PLC:plcstart


## Check Status/Logs:plcstatus
plclogs

Follow prompts to edit employees.json, production.json, or total_count.json.


## Run a Shot:
In standby mode, scan an authorized RFID tag to enter run mode.
Trigger a shot (via hardware sequence)—logs to data/csv/ and logs/plc.log.


## Reload Config: 

Edit production.json—auto-reloads within 60 seconds (see RELOAD_SECONDS).

## Contributing

Fork the repository and create a pull request.
Report issues via GitHub Issues.
Ensure code follows PEP 8 and includes logging for errors.

