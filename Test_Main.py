#! /usr/bin/python3

'''
Created on Jul 26, 2018

@author: profitrolle
'''
import FB_barcode_reader
import queue
from time import sleep
import logging
import FB_machine_interface
import FB_wp_interface
from FB_database_api import update_board_status, Board_status_enum


if __name__ == '__main__':
    print("ho")
    FB_barcode_reader.set_logger_level(logging.DEBUG)
    qq = queue.Queue()
    WPI = FB_wp_interface.WP_Interface()
    sleep(2)
    BBR = FB_barcode_reader.Barcode_Reader(qq)
    MCI = FB_machine_interface.Machine_interface(qq)
    while True:
        sleep(5)
        print('Waiting for the sandman')