import unittest, os, shutil

from cybercaptain.processing.country import processing_country
from cybercaptain.utils.exceptions import ValidationError

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_CONFIG_VALID_PATH = os.path.join(TESTDATA_FOLDER, 'input_data_ip_lookup.ccsf')
TESTDATA_MOCK_MAXMIND_DB = os.path.join(TESTDATA_FOLDER, 'mock_maxminddb.mmdb')

TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class ProcessingCountryTest(unittest.TestCase):
    """
    Test the processing country module.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)
    
    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_group_validate_method(self):
        # All Arguments correct defined
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "ipInputAttribute": "test",
            "outputAttribute": "test",
            "maxMindDbPath": TESTDATA_MOCK_MAXMIND_DB,
            "target":"."
        })
 
        pg = processing_country(**arguments)

        # ipInputAttribute missing
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "outputAttribute": "test",
            "maxMindDbPath": TESTDATA_MOCK_MAXMIND_DB,
            "target":"."
        })
 
        with self.assertRaises(ValidationError): 
            pg = processing_country(**arguments)
       
        # outputAttribute missing
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "ipInputAttribute": "test",
            "maxMindDbPath": TESTDATA_MOCK_MAXMIND_DB,
            "target":"."
        })
 
        with self.assertRaises(ValidationError): 
            pg = processing_country(**arguments)

        # outputAttribute nested (not allowed)
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "outputAttribute": "test.nested.test",
            "ipInputAttribute": "test",
            "maxMindDbPath": TESTDATA_MOCK_MAXMIND_DB,
            "target":"."
        })
 
        with self.assertRaises(ValidationError): 
            pg = processing_country(**arguments)

        # maxMindDbPath missing
        arguments = append_needed_args({
            "src":TESTDATA_CONFIG_VALID_PATH,
            "outputAttribute": "test.nested.test",
            "ipInputAttribute": "test",
            "target":"."
        })
 
        with self.assertRaises(ValidationError): 
            pg = processing_country(**arguments)

        # maxMindDbPath not a GeoLite2 Country DB
        arguments = append_needed_args({
            "src": TESTDATA_CONFIG_VALID_PATH,
            "outputAttribute": "test.nested.test",
            "ipInputAttribute": "test",
            "maxMindDbPath": "notamaxmind_db.xzy",
            "target":"."
        })
 
        with self.assertRaises(ValidationError): 
            pg = processing_country(**arguments)

        # maxMindDbPath not existing
        arguments = append_needed_args({
            "src": TESTDATA_CONFIG_VALID_PATH,
            "outputAttribute": "test.nested.test",
            "ipInputAttribute": "test",
            "maxMindDbPath": "notamaxmind_db.mmdb",
            "target":"."
        })
 
        with self.assertRaises(ValidationError): 
            pg = processing_country(**arguments)