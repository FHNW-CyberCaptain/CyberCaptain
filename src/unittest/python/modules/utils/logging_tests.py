import unittest, os, shutil

from cybercaptain.utils.logging import setup_logger, shutdown_logger

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

class UtilsLoggingTest(unittest.TestCase):
    """
    Test the utils logging module.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        shutdown_logger()
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)
    
    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)
        setup_logger(debug=False, log_location=None)

    def test_utils_logging_class(self):
        # Test Without Stdout FileHandler
        logger = setup_logger(debug=False, log_location=TESTDATA_GEN_OUTPUT_FOLDER)
        no_debug_length = len(logger.handlers)
        self.assertEqual(no_debug_length, 1)
        shutdown_logger()

        # Test With Debug Stdout FileHandler, Should Be More FH now
        logger = setup_logger(debug=True, log_location=TESTDATA_GEN_OUTPUT_FOLDER)
        self.assertEqual(len(logger.handlers), 2)
        shutdown_logger()