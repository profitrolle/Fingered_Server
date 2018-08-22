#! /usr/bin/python3

import time
import threading
import queue
from select import select
from evdev import InputDevice, ecodes, categorize, list_devices
import logging
import sys
# Local import
from FB_logging import logging_handler
from FB_database_api import find_board_from_barcode

# Logging utilities
logging.basicConfig(format='[%(module)s][%(levelname)s][%(funcName)s]%(asctime)s %(message)s')
barcode_reader_logger = logging.Logger('bcr_logger')
barcode_reader_logger.setLevel(logging.INFO)
barcode_reader_logger.addHandler(logging_handler)

# Dic for barcode scanner input
CODE_MAP_CHAR = {
    'KEY_KP4': "4",
    'KEY_KP5': "5",
    'KEY_KP6': "6",
    'KEY_KP7': "7",
    'KEY_KP0': "0",
    'KEY_KP1': "1",
    'KEY_KP2': "2",
    'KEY_KP3': "3",
    'KEY_KP8': "8",
    'KEY_KP9': "9",
    'KEY_5': "5",
    'KEY_4': "4",
    'KEY_7': "7",
    'KEY_6': "6",
    'KEY_1': "1",
    'KEY_0': "0",
    'KEY_3': "3",
    'KEY_2': "2",
    'KEY_9': "9",
    'KEY_8': "8",
}

# Current barcode reader name
BARCODE_SCANNER_NAME = "Datalogic Scanning, Inc. Handheld Barcode Scanner"


def set_logger_level(p_level):
    barcode_reader_logger.setLevel(p_level)


def check_product_barcode(p_barcode):
    barcode_product = find_board_from_barcode(p_barcode)
    if barcode_product:
        barcode_reader_logger.info(
            "Product found corresponding to the barcode %s.",
            p_barcode)
        return p_barcode
    else:
        barcode_reader_logger.error(
            "No product corresponds to the barcode %s - not trating the barcode.",
            p_barcode)
        return None


def check_position_barcode(p_barcode):
    if True:
        return p_barcode
    else:
        return None 


def parse_key_to_char(val):
    return CODE_MAP_CHAR[val] if val in CODE_MAP_CHAR else ""


def find_barcode_device():
    devices = map(InputDevice, list_devices())
    dev = None
    for device in devices:
        barcode_reader_logger.debug("Devices connected : %s ", devices)
        if device.name == BARCODE_SCANNER_NAME:
            dev = InputDevice(device.fn)
            barcode_reader_logger.debug("Barcode device found : %s ", dev)
    return dev


class Barcode_Reader():
    '''!
    classdocs
    '''

    def __init__(self, p_queue_barcode):
        '''!
        Constructor:
        @param param: param for serial port initialization.
        '''
        # Device to listen to
        self.dev = find_barcode_device()
        if not(self.dev):
            barcode_reader_logger.error("No device found, unable to scan barcodes. I'm not launching any thread.")
            sys.exit(0)
        # Last barcode read
        self.barcode = ""
        # Init state to ID reception
        self.state = "idle"
        # Queue from thrading to share the position and product data
        self.queue_barcode = p_queue_barcode
        # Create thread that read continuously the keyboards' input
        self.do_scrap_barcode = True
        self.reader_t = threading.Thread(target=self.barcode_read)
        self.reader_t.daemon = True
        self.reader_t.start()

    def stop_scrap_barcode(self):
        self.do_scrap_barcode = False
        self.serial.close()

    def start_scrap_barcode(self):
        # Create thread that read continuously the keyboards' input
        self.do_scrap_barcode = True
        self.reader_t = threading.Thread(target=self.barcode_read)
        self.reader_t.daemon = True
        self.reader_t.start()

    def update_state(self, p_new_state):
        self.state = p_new_state

    def on_new_barcode(self):
        # Check barcode validity
        if self.state == 'idle':
            self.product = check_product_barcode(self.barcode)
            if self.product:
                barcode_reader_logger.debug("Found new product barcode.")
                self.update_state('waiting_for_position')
            else:
                barcode_reader_logger.debug("Invalid product barcode, staying in idle state.")
            # Upadte state and wait for position barcode
        elif self.state == 'waiting_for_position':
            self.position = check_position_barcode(self.barcode)
            if self.position:
                barcode_reader_logger.debug("Found new position barcode, adding to queue.")                
                # Call the callback when the barcodes are ok
                self.queue_barcode.put([self.position, self.product])
            else:
                barcode_reader_logger.debug("Invalid position barcode, back to idle state.")
            # Reset state
            self.update_state('idle')
            # Reset product and position
            self.position = ""
        else:
            # Reset state
            self.update_state('idle')
            # Reset product and position
            self.position = ""
        self.barcode = ""

    def barcode_read(self):
        barcode_reader_logger.debug("Starting barcode scrapper thread.")        
        while self.do_scrap_barcode:
            r, w, x = select([self.dev], [], [])
            for event in self.dev.read():
                data = categorize(event)
                if event.type == ecodes.EV_KEY:
                    if (data.keycode == "KEY_ENTER") and (data.keystate == data.key_up):
                        barcode_reader_logger.debug("New barcode detected. [%s]", self.barcode)        
                        self.on_new_barcode()
                    if data.keystate == data.key_up:
                        self.barcode += parse_key_to_char(data.keycode)


if __name__ == "__main__":
    ser = Barcode_Reader()
    while True:
        print("Waiting for barcode")
        time.sleep(10)

