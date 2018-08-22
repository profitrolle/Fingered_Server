'''
Created on Jul 26, 2018

@author: profitrolle
'''
import threading
import logging
import json
from FB_logging import logging_handler

#Logging utilities
logging.basicConfig(format='[%(module)s][%(levelname)s][%(funcName)s]%(asctime)s %(message)s')
gcode_updater_logger = logging.Logger('gcu_logger')
gcode_updater_logger.setLevel(logging.INFO)
gcode_updater_logger.addHandler(logging_handler)

    def set_logger_level(p_level):
        gcode_updater_logger.setLevel(p_level)
    