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
                     'src': '.',
                     'keyAttributes': 'Cruiser',
                     'attributesDiff': 'Sail',
                     'target': '.'}
        self.processing = processing_diff(**arguments)

    def test_empty_arguments(self):
        """
        Test if the validation works.
        """
        arg1 = {'keyAttributes': 'Cruiser',
                'attributesDiff': 'Sail',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg1)

        arg2 = {'src': '.',
                'attributesDiff': 'Sail',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg2)

        arg3 = {'src': '.',
                'keyAttributes': 'Cruiser',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg3)

        arg4 = {'src': '.',
                'keyAttributes': 'Cruiser',
                'attributesDiff': 'Sail'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg4)
