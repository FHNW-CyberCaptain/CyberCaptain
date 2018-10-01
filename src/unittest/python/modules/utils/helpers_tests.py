import unittest, os

from cybercaptain.utils.helpers import str2bool, fileExists, is_valid_url, make_sha1, keyGen, genBTree
TESTDATA_OUT_FILENAME = os.path.join(os.path.dirname(__file__), '../assets/utilsHelpersTestFile.ccc')
TESTDATA_CONFIG_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_CONFIG_VALID_PATH = os.path.join(TESTDATA_CONFIG_FOLDER, 'ProcessingJoinTest.cctf')

class UtilsHelpersTest(unittest.TestCase):
    """
    Test the utils helper module.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        open(TESTDATA_OUT_FILENAME, 'a').close()

    def tearDown(self):
        try:
            os.remove(TESTDATA_OUT_FILENAME)
        except OSError as oserr:
            pass

    def test_utils_helpers_class(self):
        # Test File exists method
        self.assertEqual(fileExists("IAMNOTEXISTING.ccc"), False)
        self.assertEqual(fileExists(TESTDATA_OUT_FILENAME), True)

        # Test Str2Bool Method
        self.assertEqual(str2bool("yes"), True)
        self.assertEqual(str2bool("true"), True)
        self.assertEqual(str2bool("t"), True)
        self.assertEqual(str2bool("1"), True)
        self.assertEqual(str2bool("no"), False)
        self.assertEqual(str2bool("XYZ"), False)
        # Not a string given
        with self.assertRaises(ValueError): 
            str2bool(100)

        # Test is_valid_url Method
        self.assertEqual(is_valid_url("THISISNOTSAURL.json"), False)
        self.assertEqual(is_valid_url("http://thisisavalidurlbutnotexisting1234.com"), True)
        self.assertEqual(is_valid_url("https://www.google.com"), True)

        # Test make_sha1 Method
        self.assertEqual(make_sha1("test"), "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3")

    def testBTreeGen(self):
        """
        Tests if the B-Tree is generated correctly.
        """
        b_tree = genBTree(TESTDATA_CONFIG_VALID_PATH, ["name"])
        self.assertEqual(list(b_tree.items()), [("Luffy", {"name": "Luffy", "bounty": 500000000}), ("Nami", {"name": "Nami", "bounty": 66000000}), ("Zoro", {"name": "Zoro", "bounty": 320000000})])

    def testKeyGen(self):
        """
        Tests if the keys are generated properly.
        """
        key = keyGen(["name", "bounty"], {"name": "Luffy", "bounty": 500000000})
        self.assertEqual(key, "Luffy500000000")

        key = keyGen(["name"], {"name": "Luffy", "bounty": 500000000})
        self.assertEqual(key, "Luffy")
