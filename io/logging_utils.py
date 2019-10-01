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
