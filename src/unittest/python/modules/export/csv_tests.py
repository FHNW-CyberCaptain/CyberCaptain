import unittest, os, shutil

from cybercaptain.export.csv import export_csv
from cybercaptain.utils.jsonFileHandler import json_file_reader
from cybercaptain.utils.exceptions import ConfigurationError

TESTDATA_CONFIG_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_VALID_PATH = os.path.join(TESTDATA_CONFIG_FOLDER, 'export_csv_json_test_file.json')

TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_CONFIG_FOLDER, 'output')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot':os.path.join(os.path.dirname(__file__), '../assets/output'), 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class ExportCSVSimpleUtilTest(unittest.TestCase):
    """
    Test the CSV export simple utils.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)

        arguments = append_needed_args({
            "src":".",
            "target":".",
            "exportedAttributes":"all"
        })

        self.ec = export_csv(**arguments)

    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_get_value_from_nested_dict(self):
        """
        Tests if the correct value is returned.
        """
        exp_val = "Blackbeard"
        att = "Ship.Captain.Name"
        dic = {"Ship" : {"Captain" : {"Name" : exp_val}}}

        act_val = self.ec.getValueFromDict(dic, att)

        self.assertEqual(act_val, exp_val)

    def test_get_value_from_dict(self):
        """
        Tests if the correct value is returned.
        """
        exp_val = "Captain"
        att = "Rank"
        dic = {"Rank" : exp_val}

        act_val = self.ec.getValueFromDict(dic, att)

        self.assertEqual(act_val, exp_val)

    def test_get_keys_from_dict(self):
        """
        Tests if the correct keys are returned.
        """
        exp_val = ["Ship", "Ship.Captain", "Ship.Captain.Name"]
        dic = {"Ship" : {"Captain" : {"Name" : "Blackbeard"}}}
        act_val = self.ec.getKeysFromDict(dic)

        self.assertEqual(act_val.sort(), exp_val.sort()) # only the content must be the same, how it is arranged does not matter

    def test_get_all_keys_from_flie(self):
        """
        Tests if all keys from the file are found.
        """
        jfr = json_file_reader(TESTDATA_VALID_PATH)
        exp_val = ["Ship", "Ship.Captain", "Ship.Captain.Name"]
        act_val = self.ec.getAllKeysFromFile(jfr)

        self.assertEqual(act_val.sort(), exp_val.sort()) # only the content must be the same, how it is arranged does not matter

class ExportCSVAdvancedUtilTest(unittest.TestCase):
    """
    Test the CSV advanced utils.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_get_attributes_with_list(self):
        """
        Test the get Attributes method with a given list.
        """
        exp_val = ["Ship", "Ship.Captain", "Ship.Captain.Name"]
        arguments = append_needed_args({
            "src":".",
            "target":".",
            "exportedAttributes":exp_val
        })

        ec = export_csv(**arguments)
        act_val = ec.getAttributes(TESTDATA_VALID_PATH)
        self.assertEqual(act_val.sort(), exp_val.sort()) # only the content must be the same, how it is arranged does not matter

    def test_get_attributes_with_int(self):
        """
        Test the get Attributes method with a given integer.
        """
        exp_val = ["Ship", "Ship.Captain", "Ship.Captain.Name"]
        arguments = append_needed_args({
            "src":".",
            "target":".",
            "exportedAttributes":2
        })

        ec = export_csv(**arguments)
        act_val = ec.getAttributes(TESTDATA_VALID_PATH)
        self.assertEqual(act_val.sort(), exp_val.sort()) # only the content must be the same, how it is arranged does not matter

    def test_get_attributes_with_str_all(self):
        """
        Test the get Attributes method with a given integer.
        """
        exp_val = ["Ship", "Ship.Captain", "Ship.Captain.Name"]
        arguments = append_needed_args({
            "src":".",
            "target":".",
            "exportedAttributes":"all"
        })

        ec = export_csv(**arguments)
        act_val = ec.getAttributes(TESTDATA_VALID_PATH)
        self.assertEqual(act_val.sort(), exp_val.sort()) # only the content must be the same, how it is arranged does not matter
