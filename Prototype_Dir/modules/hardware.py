# hardware.py
from gpiozero import OutputDevice, Button
from Prototype_Dir.lib import I2C_LCD_driver
from mfrc522 import SimpleMFRC522
from config import RELAY_PINS, BUTTON_PINS


class Hardware:
    def __init__(self, triggers=1):
        # Relays (8)
        self.relays = [OutputDevice(pin, active_high=False) for pin in RELAY_PINS]

        # Buttons
        self.button_1 = Button(BUTTON_PINS["red"])  # Red
        self.button_2 = Button(BUTTON_PINS["green"])  # Green
        self.rfid_bypass = Button(BUTTON_PINS["bypass"], pull_up=True)
        self.trigger_1 = Button(BUTTON_PINS["trigger_1"], pull_up=True)
        if triggers == 2:
            self.trigger_2 = Button(BUTTON_PINS["trigger_2"], pull_up=True)

        # LCD (I2C on GPIO 2, 3)
        self.lcd = I2C_LCD_driver.lcd()

        # RFID (SPI, initialized later)
        self.reader = None
        self.reader_exists = False

    def init_reader(self):
        """Initialize or reset RFID reader."""
        if self.reader_exists:
            self.reader.READER.spi.close()
            del self.reader
        self.reader = SimpleMFRC522()
        self.reader_exists = True
        return self.reader

    def cleanup(self):
        """Turn off all relays."""
        for relay in self.relays:
            relay.off()

    def close(self):
        try:
            self.cleanup()
            if hasattr(self, 'reader') and self.reader is not None:  # Check if reader exists
                self.reader.READER.spi.close()
                del self.reader
                self.reader_exists = False
            self.lcd.clear()
        except Exception as e:
            print(f"Close failed: {e}")