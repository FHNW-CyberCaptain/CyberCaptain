import unittest, os, shutil, requests, responses, shodan
from unittest.mock import patch, MagicMock                                       

from cybercaptain.store.shodan import store_shodan
from cybercaptain.utils.exceptions import ValidationError

TEST_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '../assets/output')
TEST_INPUT_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')

# Output files to be generated
TESTDATA_OUTPUT_IPLOOKUP = os.path.join(TEST_OUTPUT_FOLDER, "test_shodan_iplookup_gen.cctf")
TESTDATA_OUTPUT_SEARCHQUERY1 = os.path.join(TEST_OUTPUT_FOLDER, "test_shodan_searchquery_gen_1.cctf")
TESTDATA_OUTPUT_SEARCHQUERY2 = os.path.join(TEST_OUTPUT_FOLDER, "test_shodan_searchquery_gen_2.cctf")

# Output files to test against
TESTDATA_OUTPUT_COR_IPLOOKUP = os.path.join(TEST_INPUT_FOLDER, "test_shodan_iplookup.cctf")
TESTDATA_OUTPUT_COR_IPLOOKUP2 = os.path.join(TEST_INPUT_FOLDER, "test_shodan_iplookup_2.cctf")
TESTDATA_OUTPUT_COR_SEARCHQUERY1 = os.path.join(TEST_INPUT_FOLDER, "test_shodan_searchquery_1.cctf")
TESTDATA_OUTPUT_COR_SEARCHQUERY2 = os.path.join(TEST_INPUT_FOLDER, "test_shodan_searchquery_2.cctf")


# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot':os.path.join(os.path.dirname(__file__), '../assets/output'), 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}


# Mocked shodan data api
class _mock_shodan_data_api():
    def __init__(self, apiKey):
        self.apiKey = apiKey

        self.cursor_count = 0
        if self.apiKey == "NEEDS_TO_FAIL": raise Exception()
    
    def host(self, ip, history=False, minify=False):
        if history:
            return {"data": [{"timestamp": "2018-06-20T22:28:09.514418", "html": "TEST", "port": 80},{"timestamp": "2018-06-19T22:28:09.514418", "html": "TEST2", "port": 80}], "ip_str": "1.1.1.1", "ports": [443, 80]}
        return {"data": [{"timestamp": "2018-06-20T22:28:09.514418", "html": "TEST", "port": 80}], "ip_str": "1.1.1.1", "ports": [443, 80]}

    def search_cursor(self, query, minify=False, retries=1):        
        return [
            {"hostnames":[], "port": 80, "location":{"country_code":"CH"}, "ip_str": "1.1.1.1"},
            {"hostnames":[], "port": 443, "location":{"country_code":"JP"}, "ip_str": "1.1.1.2"},
            {"hostnames":[], "port": 443, "location":{"country_code":"DE"}, "ip_str": "1.1.1.3"},
            {"hostnames":[], "port": 80, "location":{"country_code":"US"}, "ip_str": "1.1.1.4"},
            {"hostnames":[], "port": 80, "location":{"country_code":"FR"}, "ip_str": "1.1.1.5"},
            {"hostnames":[], "port": 80, "location":{"country_code":"IT"}, "ip_str": "1.1.1.6"}
        ]

# Shodan Tests
class StoreShodanTest(unittest.TestCase):
    """
    Test the store processing shodan module.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUp()

    def setUp(self):
        if not os.path.exists(TEST_OUTPUT_FOLDER):
            os.makedirs(TEST_OUTPUT_FOLDER)

        # Test inject_additional_tasks Method With Mocked Class
        self.old_shodan_class = shodan.Shodan
        shodan.Shodan = _mock_shodan_data_api

    def tearDown(self):
        shutil.rmtree(TEST_OUTPUT_FOLDER)
        shodan.Shodan = self.old_shodan_class

    def test_shodan_ts_is_newer(self):
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "target":"."
        })

        ss = store_shodan(**arguments)

        self.assertEquals(ss.shodan_ts_is_newer('2018-06-20T22:28:09.514418','2018-06-20T23:29:09.514418'), False)
        self.assertEquals(ss.shodan_ts_is_newer('2018-06-20T23:29:09.514418','2018-06-20T22:28:09.514418'), True)

    def test_shodan_run_method(self):
        # Test Run Method With Mocked Class
        #old_shodan_class = shodan.Shodan
        #shodan.Shodan = _mock_shodan_data_api

        # Test Wrong API Key - Run Returns False Cause Of Exception
        arguments = append_needed_args({
            "apiKey":"NEEDS_TO_FAIL",
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.run(), False)

        # Test IP Lookup - Port 80 (exists)
        arguments = append_needed_args({
            "apiKey":"XY",
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.run(), True)

        with open(TESTDATA_OUTPUT_COR_IPLOOKUP,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_IPLOOKUP,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        self.assertEquals(ss.run(), False) # 2nd run fails as we processed same TS already

        # Test IP Lookup - get_ip_lookup_data_by_dataset_ts port 80
        arguments = append_needed_args({
            "apiKey":"XY",
            "type": "ip_lookup",
            "getByDatasetTs": "2018-06-19T22:28:09.514418",
            "ip": "1.1.1.1",
            "port": 80,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.run(), True)

        with open(TESTDATA_OUTPUT_COR_IPLOOKUP2,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_IPLOOKUP,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        self.assertEquals(ss.run(), False) # 2nd run fails as we processed same TS already

        # Test IP Lookup - not existing type
        arguments = append_needed_args({
            "apiKey":"XY",
            "type": "ip_lookup",
            "getByDatasetTs": "2018-06-19T22:28:09.514418",
            "ip": "1.1.1.1",
            "port": 80,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        ss.type = "NOTEXISTING"
        self.assertEquals(ss.run(), False)


        # Test IP Lookup - Port 9999 (not exists in lookup)
        arguments = append_needed_args({
            "apiKey":"XY",
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 9999,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.run(), False)

        # Test IP Lookup - Port 443 existing but no data available
        arguments = append_needed_args({
            "apiKey":"XY",
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 443,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.run(), False)

        arguments = append_needed_args({
            "apiKey":"XY",
            "type": "ip_lookup",
            "getByDatasetTs": "2018-06-19T22:28:09.514418",
            "ip": "1.1.1.1",
            "port": 443,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.run(), False)


        # Test Search Query Cursor - Limit 1
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "query": "test",
            "limit": 1,
            "minify": False,
            "retries": 10,
            "target": TESTDATA_OUTPUT_SEARCHQUERY1
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.run(), True)

        with open(TESTDATA_OUTPUT_COR_SEARCHQUERY1,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_SEARCHQUERY1,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

        # Test Search Query Cursor - Limit 4
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "query": "test",
            "limit": 4,
            "minify": False,
            "retries": 10,
            "target": TESTDATA_OUTPUT_SEARCHQUERY2
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.run(), True)

        with open(TESTDATA_OUTPUT_COR_SEARCHQUERY2,'r') as f:
            expected_output = f.read()

        with open(TESTDATA_OUTPUT_SEARCHQUERY2,'r') as f2:
            output = f2.read()

        self.assertMultiLineEqual(expected_output, output)

    def test_shodan_validate_method(self):
        # ip_lookup - All parameters existing - no exception should be raised
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "target":"."
        })

        ss = store_shodan(**arguments)

        # search_query - All parameters existing - no exception should be raised
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "query": "xy EQ 12",
            "limit": 100,
            "minify": False,
            "retries": 10,
            "target":"."
        })

        ss = store_shodan(**arguments)

        # apiKey not defined
        arguments = append_needed_args({
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "history": False,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # type not defined
        arguments = append_needed_args({
            "apiKey":"xy",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # type not ip_lookup or search_query
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "NOTEXIST",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # ip_lookup - ip not defined
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "ip_lookup",
            "getByLatest": "True",
            "port": 80,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # ip_lookup - get by latest and get by timestamp not defined
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "ip_lookup",
            "ip": "1.1.1.1",
            "port": 80,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # ip_lookup - port not defined
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # ip_lookup - getMissingDatasets & getAllMissingDatasets defined (only one possible)
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "ip_lookup",
            "getByLatest": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "getMissingDatasets": "True",
            "getAllMissingDatasets": "True",
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)



        # ip_lookup - history not defined
        #arguments = append_needed_args({
        #    "apiKey":"xy",
        #    "type": "ip_lookup",
        #    "ip": "1.1.1.1",
        #    "target":"."
        #})

        #with self.assertRaises(ValidationError):
        #    ss = store_shodan(**arguments)

        # search_query - query not defined
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "limit": 100,
            "minify": False,
            "retries": 10,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # search_query - limit not defined
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "query": "xy EQ 12",
            "minify": False,
            "retries": 10,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # search_query - minify not defined
        #arguments = append_needed_args({
        #    "apiKey":"xy",
        #    "type": "search_query",
        #    "query": "xy EQ 12",
        #    "limit": 100,
        #    "retries": 10,
        #    "target":"."
        #})

        #with self.assertRaises(ValidationError):
        #    ss = store_shodan(**arguments)

        # search_query - retries not defined
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "query": "xy EQ 12",
            "limit": 100,
            "minify": False,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # search_query - trying to use getMissingDataSets
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "query": "xy EQ 12",
            "getMissingDatasets": "True",
            "limit": 100,
            "minify": False,
            "retries": 10,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

        # search_query - trying to use getAllMissingDataSets
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "query": "xy EQ 12",
            "getAllMissingDatasets": "True",
            "limit": 100,
            "minify": False,
            "retries": 10,
            "target":"."
        })

        with self.assertRaises(ValidationError):
            ss = store_shodan(**arguments)

    def test_shodan_inject_additional_tasks_method(self):
        # Test injecting addiitonal tasks found via API (get datasets between last run and newest)
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "ip_lookup",
            "getByLatest": "True",
            "getMissingDatasets": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        additional_tasks = ss.inject_additional_tasks()
        self.assertEquals(len(additional_tasks), 0)

        # Test injecting addiitonal tasks found via API (get all datasets from start)
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "ip_lookup",
            "getByLatest": "True",
            "getAllMissingDatasets": "True",
            "ip": "1.1.1.1",
            "port": 80,
            "target": TESTDATA_OUTPUT_IPLOOKUP
        })

        ss = store_shodan(**arguments)
        additional_tasks = ss.inject_additional_tasks()
        self.assertEquals(len(additional_tasks), 2)

        # Test injecting addiitonal tasks with another type than ip lookup
        arguments = append_needed_args({
            "apiKey":"xy",
            "type": "search_query",
            "query": "xy EQ 12",
            "limit": 100,
            "minify": False,
            "retries": 10,
            "target":"."
        })

        ss = store_shodan(**arguments)
        self.assertEquals(ss.inject_additional_tasks(), False)