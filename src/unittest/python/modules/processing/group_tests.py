import unittest, os, shutil

from cybercaptain.processing.group import processing_group
from cybercaptain.utils.exceptions import ValidationError

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_CONFIG_VALID_PATH = os.path.join(TESTDATA_FOLDER, 'input_data_10_cleaned.ccsf')

TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'joinOutput')
TESTDATA_TARGET_FILENAME = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'ProcessingGroupTest.cctf')

def append_needed_args(existing_args):
    """
    Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
    """
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class ProcessingGroupTest(unittest.TestCase):
    """
    Test the store processing group module.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        """
        Set Up Stuff.
        """
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)

    def tearDown(self):
        """
        Tear Down Stuff.
        """
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_group_validate_method(self):
        """
        Test the group validation method.
        """
        # Missing GroupBy Agument
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "target":"."
        })

        with self.assertRaises(ValidationError):  
            pg = processing_group(**arguments)

    def test_group_run_method(self):
        """
        Test the group test method.
        """
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "groupby": "data.xssh.server_id.software",
            "target":TESTDATA_TARGET_FILENAME
        })

        pg2 = processing_group(**arguments)
        pg2.run()

        with open(TESTDATA_FOLDER+"/processingGroupRunTest.cctf-pg1", 'r') as f:
            expected_output = f.read()

        with open(TESTDATA_TARGET_FILENAME, 'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

    def test_dict_to_list(self):
        """
        Test if the dictToList function works.
        """
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "groupby": "data.xssh.server_id.software",
            "target":TESTDATA_TARGET_FILENAME
        })

        pg2 = processing_group(**arguments)

        _dict = {'CHE': 420, 'USA': 0, 'RUS': 100}
        expected = [{'group':'CHE', 'count': 420}, {'group':'USA', 'count': 0}, {'group':'RUS', 'count': 100}]
        got = pg2.dictToList(_dict)
        self.assertEqual(expected, got)
