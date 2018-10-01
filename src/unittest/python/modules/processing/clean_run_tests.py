import unittest, json, os, glob, shutil

from cybercaptain.processing.clean import processing_clean

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

TESTDATA_SRC_FILENAME = os.path.join(TESTDATA_FOLDER, 'input_data_10.ccsf') # Consists of lines with missing keys etc
TESTDATA_TARGET_FILENAME = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'ProcessingCleanRunTestOuts.cctf')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class ProcessingCleanRunTest(unittest.TestCase):
    """
    Test the processing clean for the run method
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)
    
    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_run(self):
        """
        Test if the cleaners run method runs correct
        """

        # Test to keep values and remove lines with missing keys
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'format': 'json',
                     'keep': ['data.xssh.server_id.software', 'timestamp'],
                     'removeMissingKeys': 'true',
                     'target': TESTDATA_TARGET_FILENAME})
        pc1 = processing_clean(**arguments)
        pc1.run()

        with open(TESTDATA_FOLDER+'/processingCleanRunTest.cctf-pc1','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to keep values and ignore missing keys
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'format': 'json',
                     'keep': ['data.xssh.server_id.software', 'timestamp'],
                     'ignoreMissingKeys': 'true',
                     'target': TESTDATA_TARGET_FILENAME})
        pc2 = processing_clean(**arguments)
        pc2.run()

        with open(TESTDATA_FOLDER+'/processingCleanRunTest.cctf-pc2','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to drop values and remove lines with missing keys
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'format': 'json',
                     'drop': ['data.xssh.server_id.software', 'timestamp'],
                     'removeMissingKeys': 'true',
                     'target': TESTDATA_TARGET_FILENAME})
        pc3 = processing_clean(**arguments)
        pc3.run()

        with open(TESTDATA_FOLDER+'/processingCleanRunTest.cctf-pc3','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        # Test to drop values and ignore missing keys
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'format': 'json',
                     'drop': ['data.xssh.server_id.software', 'timestamp'],
                     'ignoreMissingKeys': 'true',
                     'target': TESTDATA_TARGET_FILENAME})
        pc4 = processing_clean(**arguments)
        pc4.run()

        with open(TESTDATA_FOLDER+'/processingCleanRunTest.cctf-pc4','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to keep/drop values which contain missing keys but no ignore/removeMissingKeys defined
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'format': 'json',
                     'keep': ['data.xssh.server_id.software', 'timestamp'],
                     'target': TESTDATA_TARGET_FILENAME})
        pc5 = processing_clean(**arguments)
        with self.assertRaises(KeyError):
            pc5.run()

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'format': 'NOTIMPLEMENTED_FORMAT',
                     'keep': ['data.xssh.server_id.software', 'timestamp'],
                     'removeMissingKeys': 'true',
                     'target': TESTDATA_TARGET_FILENAME})
        pc6 = processing_clean(**arguments)
        with self.assertRaises(NotImplementedError):
            pc6.run()
