'''
Created on Jul 27, 2018

@author: profitrolle
'''
import threading
import logging
import os
from os.path import isfile, join
import time
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# local import
from FB_database_api import get_pending_board, find_board_from_barcode, update_board_status, Board_status_enum, refresh_session
from FB_barcode_util import do_product_barcode, get_position_barcode_info, get_product_barcode_info
from FB_logging import logging_handler
from g_objects import G_Objects

# Logging utilities
logging.basicConfig(format='[%(module)s][%(levelname)s][%(funcName)s]%(asctime)s %(message)s')
machine_interface_logger = logging.Logger('mci_logger')
machine_interface_logger.setLevel(logging.INFO)
machine_interface_logger.addHandler(logging_handler)


def set_logger_level(p_level):
    machine_interface_logger.setLevel(p_level)


MAX_NUMBER_OF_WORKS = 5
TIMEOUT_GET_BARCODE = 600  # [secondes] -> 10 min
BASE_PATH = "/home/profitrolle/Documents/GCODE/"
PENDING_GCODE_PATH = BASE_PATH + "pending_gcode/"
CURRENT_WORK_PATH = BASE_PATH + "current_work_gcode/"
OLD_GCODE_PATH = BASE_PATH + "old_gcode/"


def get_id_from_file_name(p_name):
    barcode = p_name.split('/')[-1].split('.')[0]
    _, _, _, board_id = get_product_barcode_info(barcode)
    return board_id


class Machine_interface(FileSystemEventHandler):
    '''
    classdocs
    '''

    def __init__(self, p_queue_barcode):
        '''
        Constructor
        '''
        self.free_place = MAX_NUMBER_OF_WORKS
        self.board_is_waiting = False
        
        # Queue for barcodes
        self.barcode_queue = p_queue_barcode
        
        # Lock for files access
        self.file_lock = threading.Lock()
        
        # Get an instance of the poutre maker, for GCODE creation
        self.poutre_maker = G_Objects(p_path=PENDING_GCODE_PATH)
        
        # Create thread that waits continuously for new board
        self.do_wait_for_board = True
        self.waitint_for_board_t = threading.Thread(target=self.wait_for_board)
        self.waitint_for_board_t.daemon = True
        self.waitint_for_board_t.start()
        
        # Launch the file observer that supervise job dones
        self.file_observer()
    
    def wait_for_board(self):
        # This thread is
        while self.do_wait_for_board:
            # Not using queue because if the program crashes, queue is lost,
            # Scrapping on object   creation
            # Then read the DB on timeout & on queue read
            # If there is a free spot, start the processing, else, wait for a free spot
            if self.is_free_spot():
                self.board_processed = get_pending_board()
                if self.board_processed:
                    machine_interface_logger.info("New pending board found with id == %d", self.board_processed.id)
                    self.on_new_board()
                else:
                    machine_interface_logger.info("No pending board found ... waiting")
                    time.sleep(10)
                    refresh_session()
    
    def is_free_spot(self):
        files_in_wd = [f for f in os.listdir(CURRENT_WORK_PATH) if isfile(join(CURRENT_WORK_PATH, f))]
        files_in_pd = [f for f in os.listdir(PENDING_GCODE_PATH) if isfile(join(PENDING_GCODE_PATH, f))]
        number_of_files = MAX_NUMBER_OF_WORKS - len(files_in_wd) - len(files_in_pd)
        return (number_of_files > 0)

    def is_machine_free(self):
        files_in_wd = os.listdir(CURRENT_WORK_PATH)
        if len(files_in_wd):
            return False
        return True

    def on_new_board(self):
        # Start processing board
        # Update board status
        update_board_status(self.board_processed.id, Board_status_enum.waiting_machine)
        # Print barcode for the product
        do_product_barcode(self.board_processed.barcode)
        # Start barcode consumer thread
        self.barcode_consume()

    def start_barcode_consumer(self):
        # Create thread that waits on new barcode
        self.activate_on_new_barcode = True
        self.on_new_barcode_t = threading.Thread(target=self.barcode_consume)
        self.on_new_barcode_t.daemon = True
        self.on_new_barcode_t.start()

    def stop_barcode_consumer(self):
        self.activate_on_new_barcode = False

    def barcode_consume(self):
        machine_interface_logger.debug("Waiting to process barcode.")
        # Empty queue -> The queue is used only on request from the consumer, no
        # barcode should be received otherwise.
        while not self.barcode_queue.empty():
            self.barcode_queue.get()
        # Wait for new barcode
        try:
            self.position_barcode, self.product_barcode = self.barcode_queue.get(timeout=TIMEOUT_GET_BARCODE)
        except queue.Empty:
            machine_interface_logger.info("Got no barcode while waiting for one... Stop waisting my time, I quit.")
        else:
            machine_interface_logger.info("Consuming data %s %s", self.position_barcode, self.product_barcode)
            x_offset, y_offset = get_position_barcode_info(self.position_barcode)
            position = {
                "x_offset": x_offset,
                "y_offset": y_offset
                }
            board = find_board_from_barcode(self.product_barcode)
            self.create_gcode_conf(position, board)
            # Move new file to treat
            if self.is_machine_free():
                if self.file_lock.acquire(False):
                    files_in_pd = [f for f in os.listdir(PENDING_GCODE_PATH) if isfile(join(PENDING_GCODE_PATH, f))]
                    os.rename(PENDING_GCODE_PATH + files_in_pd[0], CURRENT_WORK_PATH + files_in_pd[0])
                    machine_interface_logger.info("Gcode file for product %s moved to work directory", self.product_barcode)
                    self.file_lock.release()
            else:
                machine_interface_logger.info("Machine is busy, GCODE file stays in pending dir")

    def create_gcode_conf(self, p_position, p_board):
        machine_interface_logger.info("New Gcode file created for product %s at position %s", p_board.id, p_position)
        hole_list = p_board.holes
        for hole in hole_list:
            hole["x_position"] += p_position["x_offset"]
            hole["y_position"] += p_position["y_offset"]
        self.poutre_maker.set_gcode_file_name(str(p_board.barcode))
        self.poutre_maker.make_holes(hole_list)
    
    def file_observer(self):
        observer = Observer()
        observer.schedule(self, CURRENT_WORK_PATH)
        observer.start()
        observer.join()

    def on_created(self, event):
        file_path = event.src_path
        file_name = file_path.split('/')[-1]
        machine_interface_logger.info("New Gcode file detected in work directory (%s)", file_name)
        # Update board status
        update_board_status(get_id_from_file_name(file_name), Board_status_enum.processing)

    def on_deleted(self, event):
        file_name = event.src_path
        machine_interface_logger.info("Gcode file deleted in work directory - my work here is done")
        # Update board status
        update_board_status(get_id_from_file_name(file_name), Board_status_enum.waiting_ship)
        # relaunch
        # Move new file to treat
        if self.is_machine_free():
            if self.file_lock.acquire(False):
                files_in_pd = [f for f in os.listdir(PENDING_GCODE_PATH) if isfile(join(PENDING_GCODE_PATH, f))]
                if len(files_in_pd) > 0:
                    os.rename(PENDING_GCODE_PATH + files_in_pd[0], CURRENT_WORK_PATH + files_in_pd[0])
                    machine_interface_logger.info("Gcode file for product %s moved to work directory", self.product_barcode)
                self.file_lock.release()
