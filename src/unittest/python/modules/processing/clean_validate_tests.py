import unittest

from cybercaptain.processing.clean import processing_clean
from cybercaptain.utils.exceptions import ValidationError

class ProcessingCleanArgTest(unittest.TestCase):
    """
    Test the processing clean validation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'format': '.',
                     'keep': '.',
                     'target': '.'}
        self.processing = processing_clean(**arguments)

    def test_empty_arguments(self):
        arg1 = {'format': '.',
                'keep': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg1)

        arg2 = {'src': '.',
                'keep': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg2)

        arg3 = {'src': '.',
                'format': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg3)

        arg4 = {'src': '.',
                'format': '.',
                'keep': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg4)

        arg5 = {'src': '.',
                'format': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg5)

        arg6 = {'format': '.',
                'drop': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg6)

        # Test for drop and keep both defined
        arg7 = {'src': '.',
                'format': '.',
                'drop': '.',
                'keep': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg7)

        arg8 = {'src': '.',
                'format': '.',
                'drop': '.',
                'ignoreMissingKeys':'.',
                'removeMissingKeys':'.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg8)

        arg9 = {'src': '.',
                'format': '.',
                'drop': '.',
                'ignoreMissingKeys':1,
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg9)

        arg10 = {'src': '.',
                'format': '.',
                'drop': '.',
                'removeMissingKeys':1,
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg10)

    def test_keep_args(self):
        arg1 = {'src': '.',
                'format': '.',
                'keep': 123,
                'target': '.'}
        with self.assertRaises(ValidationError):
            self.processing.validate(arg1)

        arg2 = {'src': '.',
                'format': '.',
                'keep': 'test',
                'target': '.'}
        try:
            self.processing.validate(arg2)
        except ValidationError:
            self.fail('Exception raised')

        arg3 = {'src': '.',
                'format': '.',
                'keep': ['test', 'test2'],
                'target': '.'}
        try:
            self.processing.validate(arg3)
        except ValidationError:
            self.fail('Exception raised')

    def test_drop_args(self):
        arg1 = {'src': '.',
                'format': '.',
                'drop': 123,
                'target': '.'}
        with self.assertRaises(ValidationError):
            self.processing.validate(arg1)

        arg2 = {'src': '.',
                'format': '.',
                'drop': 'test',
                'target': '.'}
        try:
            self.processing.validate(arg2)
        except ValidationError:
            self.fail('Exception raised')

        arg3 = {'src': '.',
                'format': '.',
                'drop': ['test', 'test2'],
                'target': '.'}
        try:
            self.processing.validate(arg3)
        except ValidationError:
            self.fail('Exception raised')