import logging

logging_handler = logging.StreamHandler()
logging_handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('[%(module)s][%(levelname)s][%(funcName)s]%(asctime)s %(message)s')

# add formatter to ch
logging_handler.setFormatter(formatter)

def set_console_logging_handler():
    global logging_handler
    logging_handler = logging.StreamHandler()

def set_file_logging_handler(p_file):
    global logging_handler
    logging_handler = logging.FileHandler(p_file)
