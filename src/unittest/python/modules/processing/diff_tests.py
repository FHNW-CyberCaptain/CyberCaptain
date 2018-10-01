import unittest, os

from cybercaptain.processing.diff import processing_diff
from cybercaptain.utils.exceptions import ValidationError

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')

class ProcessingDiffArgTest(unittest.TestCase):
    """
    Test the Diff validation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'projectName': 'DiffTest',
                     'projectRoot': TESTDATA_FOLDER,
                     'moduleName': 'Diff',
                     'src': TESTDATA_FOLDER + '/diff_test_0',
                     'keyAttributes': 'Cruiser',
                     'attributesDiff': 'Sail',
                     'target': '.'}
        self.processing = processing_diff(**arguments)

    def test_target_exists(self):
        """
        Test if the target_exists works.
        """
        arguments = {'projectName': 'DiffTest',
                     'projectRoot': TESTDATA_FOLDER,
                     'moduleName': 'Diff1',
                     'src': '.',
                     'keyAttributes': 'Cruiser',
                     'attributesDiff': 'Sail',
                     'target': TESTDATA_FOLDER + '/diff_test_1'}
        diff1 = processing_diff(**arguments)
        self.assertFalse(diff1.target_exists())

        arguments['src'] = TESTDATA_FOLDER + '/diff_test_2'
        arguments['target'] = TESTDATA_FOLDER + '/DiffTest'
        diff2 = processing_diff(**arguments)
        self.assertFalse(diff2.target_exists())

    def test_dataGen(self):
        """
        Test if the data generation works.
        """
        expected = {"cc_id": "id", "cc_status": "insert", "cc_time_id": "diff_test_0", "data": "this_thing"}
        got = self.processing.genDataSet("id", {"data": "this_thing"}, ["data"])
        self.assertEqual(expected, got)

        expected["cc_status"] = "abc"
        got = self.processing.genDataSet("id", {"data": "this_thing"}, ["data"], "abc")
        self.assertEqual(expected, got)

    def test_data_comparison(self):
        """
        Test if the data comparison works.
        """
        expected = {"cc_id": "id", "cc_status": "insert", "cc_time_id": "diff_test_0", "data": "this_thing"}
        old_data = {"cc_id": "id", "cc_status": "insert", "cc_time_id": "diff_test_0", "data": "this_thing"}
        new_data = {"data": "this_thing"}
        got = self.processing.compareData(old_data, new_data)
        self.assertEqual(expected, got)

        new_data = {"data": "another_thing"}
        expected = {"cc_id": "id", "cc_status": "update", "cc_time_id": "diff_test_0", "data": "another_thing", 'data_PREVIOUS': 'this_thing'}
        got = self.processing.compareData(old_data, new_data)
        self.assertEqual(expected, got)

        new_data = {"data": "another_thing"}
        old_data = {"cc_id": "id", "cc_status": "delete", "cc_time_id": "diff_test_0", "data": "another_thing"}
        expected = {"cc_id": "id", "cc_status": "insert", "cc_time_id": "diff_test_0", "data": "another_thing"}
        got = self.processing.compareData(old_data, new_data)
        self.assertEqual(expected, got)

    def test_get_data_by_attribute(self):
        """
        Test if the data is retrived correctly.
        """
        data = {"test1": "test", "test2": "another"}
        attributes = ["test1"]
        expected = {"test1": "test"}
        got = self.processing.getDataByAttributes(attributes, data)
        self.assertEqual(expected, got)
