import unittest, json, os, glob, shutil

from cybercaptain.processing.filter import processing_filter

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

TESTDATA_SRC_FILENAME = os.path.join(TESTDATA_FOLDER, 'input_data_10_cleaned.ccsf') # Consists of only cleaned lines as filtered often after clean
TESTDATA_TARGET_FILENAME = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'ProcessingFilterRunTestOuts.cctf')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class ProcessingFilterRunTest(unittest.TestCase):
    """
    Test the processing filter for the run method
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

        # Test to filter lines with an EQ
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'filterby': 'data.xssh.server_id.number',
                     'rule': 'EQ 111',
                     'target': TESTDATA_TARGET_FILENAME})
        pf1 = processing_filter(**arguments)
        #pf1.target = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER)
        pf1.run()

        with open(TESTDATA_FOLDER+'/processingFilterRunTest.cctf-pf1','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to filter lines with an GT
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'filterby': 'data.xssh.server_id.number',
                     'rule': 'GT 111',
                     'target': TESTDATA_TARGET_FILENAME})
        pf2 = processing_filter(**arguments)
        pf2.run()

        with open(TESTDATA_FOLDER+'/processingFilterRunTest.cctf-pf2','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to filter lines with an GE
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'filterby': 'data.xssh.server_id.number',
                     'rule': 'GE 111',
                     'target': TESTDATA_TARGET_FILENAME})
        pf3 = processing_filter(**arguments)
        pf3.run()

        with open(TESTDATA_FOLDER+'/processingFilterRunTest.cctf-pf3','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to filter lines with an RE
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'filterby': 'data.xssh.server_id.software',
                     'rule': 'RE OpenSSH_([7-9])',
                     'target': TESTDATA_TARGET_FILENAME})
        pf4 = processing_filter(**arguments)
        pf4.run()

        with open(TESTDATA_FOLDER+'/processingFilterRunTest.cctf-pf4','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to filter lines with an LT
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'filterby': 'data.xssh.server_id.number',
                     'rule': 'LT 111',
                     'target': TESTDATA_TARGET_FILENAME})
        pf5 = processing_filter(**arguments)
        pf5.run()

        with open(TESTDATA_FOLDER+'/processingFilterRunTest.cctf-pf5','r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to filter lines with an LE
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'filterby': 'data.xssh.server_id.number',
                     'rule': 'LE 111',
                     'target': TESTDATA_TARGET_FILENAME})
        pf6 = processing_filter(**arguments)
        pf6.run()

        with open(os.path.join(TESTDATA_FOLDER, 'processingFilterRunTest.cctf-pf6'),'r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test to filter lines with an LE
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
                     'filterby': 'data.xssh.server_id.number',
                     'rule': 'NE 111',
                     'target': TESTDATA_TARGET_FILENAME})
        pf7 = processing_filter(**arguments)
        pf7.run()

        with open(os.path.join(TESTDATA_FOLDER, 'processingFilterRunTest.cctf-pf7'),'r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

