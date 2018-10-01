import unittest, os

from cybercaptain.base import cybercaptain_base

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot':os.path.join(os.path.dirname(__file__), '../assets/output'), 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class CyberCaptainBaseTest(unittest.TestCase):
    """
    Test the cybercaptain base
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = append_needed_args({'src': '',
                     'target': os.path.realpath(__file__)})
        self.base = cybercaptain_base(**arguments)

    def test_base_class(self):
        # Test Target Exists
        self.base.target
        self.assertTrue(self.base.target_exists())
        self.base.target = "FILENOTEXISTING"
        self.assertFalse(self.base.target_exists())

        # Test Base Run
        with self.assertRaises(NotImplementedError):
            self.base.run()

        # Test Pre/Post Checks - Default implementation
        # Seperatly tested if implemented in other module
        self.assertTrue(self.base.pre_check())
        self.assertTrue(self.base.post_check())