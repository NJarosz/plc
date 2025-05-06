#!/bin/bash
LOG_DIR="/home/pi/plc/logs"
LOG_FILE="/home/pi/plc/logs/plc.log"
DATE=$(date +%m%d%Y)

sudo systemctl stop plc.service

# Move and rename the current log

if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "$LOG_DIR/plc_$DATE.log"
fi

sudo systemctl start plc.service

# Delete logs older than 7 days
find "$LOG_DIR" -type f -name "plc_*.log" -mtime +7 -delete

