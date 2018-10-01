import unittest, os, shutil

from BTrees.OOBTree import OOBTree # pylint: disable=no-name-in-module
from cybercaptain.processing.join import processing_join

TESTDATA_CONFIG_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_CONFIG_VALID_PATH = os.path.join(TESTDATA_CONFIG_FOLDER, 'ProcessingJoinTest.cctf')

class ProcessingJoinTest(unittest.TestCase):
    """
    Test the store processing join module.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'left-joinon': 'Cruiser',
                     'right-joinon': 'Cruiser',
                     'joinwith': 'Sail',
                     'target': '.'}
        self.processing = processing_join(**arguments)

    def testCorrectJoin(self):
        """
        Tests if the join works correctly.
        """
        b_tree = OOBTree()
        b_tree.update({1: "Monkey D. Luffy", 2: "Roronoa Zoro", 3: "Nami"})
        failed_counter = 0
        key = 1
        data = {"from":"East Blue"}
        (mod_data, mod_tree, failed_counter) = self.processing.join(b_tree, key, data, failed_counter)
        self.assertEqual(mod_data, {"from":"East Blue", "right_data":"Monkey D. Luffy"})
        self.assertEqual(len(mod_tree), 2)
        self.assertEqual(failed_counter, 0)

    def testFailedJoin(self):
        """
        Tests if the join works correctly.
        """
        b_tree = OOBTree()
        b_tree.update({1: "Monkey D. Luffy", 2: "Roronoa Zoro", 3: "Nami"})
        failed_counter = 0
        key = 10
        data = {"from":"East Blue"}
        (mod_data, mod_tree, failed_counter) = self.processing.join(b_tree, key, data, failed_counter)
        self.assertEqual(mod_data, {"from":"East Blue"})
        self.assertEqual(len(mod_tree), 3)
        self.assertEqual(failed_counter, 1)
