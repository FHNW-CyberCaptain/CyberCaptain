import unittest

from cybercaptain.processing.join import processing_join
from cybercaptain.utils.exceptions import ValidationError

class ProcessingJoinArgTest(unittest.TestCase):
    """
    Test the Join validation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'left-joinon': 'Cruiser',
                     'right-joinon': 'Cruiser',
                     'joinwith': 'Sail',
                     'target': '.'}
        self.processing = processing_join(**arguments)

    def test_empty_arguments(self):
        arg1 = {'left-joinon': 'Cruiser',
                'right-joinon': 'Cruiser',
                'joinwith': 'Sail',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg1)

        arg2 = {'src': '.',
                'right-joinon': 'Cruiser',
                'joinwith': 'Sail',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg2)

        arg3 = {'src': '.',
                'right-joinon': 'Cruiser',
                'left-joinon': 'Cruiser',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg3)

        arg4 = {'src': '.',
                'right-joinon': 'Cruiser',
                'left-joinon': 'Cruiser',
                'joinwith': 'Sail'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg4)

        arg5 = {'src': '.',
                'left-joinon': 'Cruiser',
                'joinwith': 'Sail',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg5)
