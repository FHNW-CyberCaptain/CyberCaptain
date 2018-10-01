"""
Testing the KV Store
"""
import unittest
import shutil
import os
from cybercaptain.utils.kvStore import kv_store

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_STORE_EXIST_FILENAME = 'kvstore_exist.ccdb'

class KvStoreTest(unittest.TestCase):
    """
    Test the k/v store class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.kvstore = kv_store(TESTDATA_FOLDER, TESTDATA_STORE_EXIST_FILENAME)

    def tearDown(self):
        pass

    def test_get_values(self):
        """
        Test the get method to get values from the existing store via key
        """

        # Get Values From Root
        self.assertEqual(self.kvstore.get("testvalue1"), 'Test')
        self.assertEqual(self.kvstore.get("testvalue2"), '1')
        self.assertEqual(self.kvstore.get("testvalue3"), ["test1", "test2", "test3"])
        self.assertEqual(self.kvstore.get("testvalue4"), 'True')

        # Get Values From Defined Section (Group)
        self.assertEqual(self.kvstore.get("testvalue2", section="test_section"), '2')
        self.assertEqual(self.kvstore.get("testvalue3", section="test_section"), ["test2", "test3", "test4"])

        # Get Values From Non Existing Keys
        self.assertEquals(self.kvstore.get("not_existing_key"), None)
        self.assertEquals(self.kvstore.get("not_existing_key", section="not_existing_group"), None)

    def test_put_values(self):
        """
        Test the put method to save values into the existing store
        """

        # Put Values To Root - No Persist
        self.assertEqual(self.kvstore.put("testvalue1", 'TestChanged'), True)
        self.assertEqual(self.kvstore.get("testvalue1"), 'TestChanged') # Should be changed but not persisted to disk yet
        self.kvstore.reload()
        self.assertEqual(self.kvstore.get("testvalue1"), 'Test') # Should be the old value again as not persisted

        self.assertEqual(self.kvstore.put("testvalue3", ['test_list']), True)
        self.assertEqual(self.kvstore.get("testvalue3"), ['test_list']) # Should be changed but not persisted to disk yet
        self.kvstore.reload()
        self.assertEqual(self.kvstore.get("testvalue3"), ["test1", "test2", "test3"]) # Should be the old value again as not persisted

        # Put Values To Root - Persist
        self.assertEqual(self.kvstore.put("testvalue1", 'TestChanged2', force=True), True)
        self.assertEqual(self.kvstore.get("testvalue1"), 'TestChanged2') # Should be changed and also be persisted after reload
        self.kvstore.reload()
        self.assertEqual(self.kvstore.get("testvalue1"), 'TestChanged2') # Also changed after reload
        self.assertEqual(self.kvstore.put("testvalue1", 'Test', force=True), True) # Reset Value
        self.kvstore.reload()

        self.assertEqual(self.kvstore.put("testvalue3", ['test_list'], force=True), True)
        self.assertEqual(self.kvstore.get("testvalue3"), ['test_list']) # Should be changed but not persisted to disk yet
        self.kvstore.reload()
        self.assertEqual(self.kvstore.get("testvalue3"), ['test_list']) # Also changed after reload
        self.assertEqual(self.kvstore.put("testvalue3", ["test1", "test2", "test3"], force=True), True)
        self.kvstore.reload()

        # Put Values To Defined Section (Group) - No Persist
        self.assertEqual(self.kvstore.put("testvalue2", '1', section="test_section"), True)
        self.assertEqual(self.kvstore.get("testvalue2", section="test_section"), '1')
        self.kvstore.reload()
        self.assertEqual(self.kvstore.get("testvalue2", section="test_section"), '2')

        # Put Values To Defined Section (Group) - Persist
        self.assertEqual(self.kvstore.put("testvalue2", '1', section="test_section", force=True), True)
        self.assertEqual(self.kvstore.get("testvalue2", section="test_section"), '1')
        self.kvstore.reload()
        self.assertEqual(self.kvstore.get("testvalue2", section="test_section"), '1')
        self.assertEqual(self.kvstore.put("testvalue2", '2', section="test_section", force=True), True)
        self.kvstore.reload()