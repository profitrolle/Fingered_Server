'''
Created on Nov 21, 2016

@author: profitrolle
'''
import logging
"""
Used for all logging
"""
# create console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '[%(module)s][%(levelname)s][%(funcName)s]%(asctime)s %(message)s')

# add formatter to ch
console_handler.setFormatter(formatter)
