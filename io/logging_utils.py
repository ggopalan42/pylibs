''' Utilities for logging '''

import os
import logging

def set_logging():
    ''' Setup logging so it works on both containers and locally

        The basic idea is to log to the specified file if os environment
        variable is set or to stdout if its not set
    '''

    if 'LOG_TO_FILE' in os.environ.keys():
        log_fn = os.environ['LOG_TO_FILE']
        # Now setup the logging to file
        logging.basicConfig(level=logging.INFO, filename=log_fn,
                            format='%(asctime)s - %(name)s - '
                            '%(levelname)s - %(message)s')
    else:
        # Else log to stdout
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - '
                            '%(levelname)s - %(message)s')

def log_if_false(status, message, log_as='error'):
    ''' Log message if status is False '''
    if not status:
        if log_as == 'error':
            logging.error(message)
        elif log_as == 'warning':
            logging.warning(message)
        elif log_as == 'info':
            logging.info(message)
        else:
            pass

def log_if_true(status, message, log_as='info'):
    ''' Log message if status is True '''
    if not status:
        if log_as == 'info':
            logging.info(message)
        else:
            pass

