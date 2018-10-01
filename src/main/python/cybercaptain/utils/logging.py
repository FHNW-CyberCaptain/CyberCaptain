"""
The logging module simply setsup the logging enviorment for CyberCaptain
"""
import logging, sys, os

def setup_logger(debug, log_location):
    """
    This function contains all the necessary steps to setup the logger.
    """
    logger = logging.getLogger('CyberCaptain')

    # Only setup our logger if not already setup
    if not len(logger.handlers):
        formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)-8s] - %(message)s')

        # Log to file if log location given
        if log_location:
            # create file handler which logs even debug messages
            fh = logging.FileHandler(os.path.join(log_location, 'cybercaptain.log'))
            fh.setLevel(logging.INFO)

            if debug: 
                logger.setLevel(logging.DEBUG)
                fh.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)
                fh.setLevel(logging.INFO)

            # create formatter and add it to the handlers
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        # Log to stdout if debug defined or log location not defined
        if debug or not log_location:
            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(formatter)
            logger.addHandler(sh)

    return logger

def shutdown_logger():
    """
    This function closes all loggers and removes the handlers.
    """
    logger = logging.getLogger('CyberCaptain')
    x = logger.handlers.copy()
    for i in x:
        logger.removeHandler(i)
        i.flush()
        i.close()