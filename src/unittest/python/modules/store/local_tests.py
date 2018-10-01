import unittest, os, shutil

from cybercaptain.store.local import store_local
from cybercaptain.utils.exceptions import ValidationError

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

TESTDATA_CONFIG_VALID_PATH = os.path.join(TESTDATA_FOLDER ,'input_data_10.ccsf')
TESTDATA_TARGET_FILENAME = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER ,'StoreLocalOuts.cctf')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class StoreLocalTest(unittest.TestCase):
    """
    Test the store processing local module.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)
    
    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_local_run_method(self):
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "format":"json",
            "target":TESTDATA_TARGET_FILENAME
        })
        sl = store_local(**arguments).run()

        with open(TESTDATA_FOLDER+"/storeLocalRunTest.cctf-sl1",'r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "format":"NOTIMPLEMENTEDFORMAT",
            "target":TESTDATA_TARGET_FILENAME
        })

        with self.assertRaises(NotImplementedError):
            sl2 = store_local(**arguments).run()

    def test_local_validate_method(self):
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "format":".",
            "target":"."
        })
        sl3 = store_local(**arguments)


        arguments = append_needed_args({
            "src":"NOTEXISTING.ccsf",
            "format":".",
            "target":"."
        })
        with self.assertRaises(ValidationError):  
            sl4 = store_local(**arguments)