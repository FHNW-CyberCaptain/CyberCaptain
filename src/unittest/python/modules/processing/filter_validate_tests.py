import unittest

from cybercaptain.processing.filter import processing_filter
from cybercaptain.utils.exceptions import ValidationError

class ProcessingFilterArgTest(unittest.TestCase):
    """
    Test the filters validation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'filterby': 'w',
                     'rule': 'GE 500',
                     'target': '.'}
        self.processing = processing_filter(**arguments)

    def test_empty_arguments(self):
        arg1 = {'filterby': 'w',
                'rule': 'GE 500',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg1)

        arg2 = {'src': '.',
                'rule': 'GE 500',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg2)

        arg3 = {'src': '.',
                'filterby': 'w',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg3)

        arg4 = {'src': '.',
                'filterby': 'w',
                'rule': 'GE 500'}

        with self.assertRaises(ValidationError):
            self.processing.validate(arg4)

    def test_rule_args(self):
        arg1 = { 'src': '.',
                 'filterby': 'w',
                 'rule': 'GE ',
                 'target': '.'}
        with self.assertRaises(ValidationError):
            self.processing.validate(arg1)

        arg2 = { 'src': '.',
                 'filterby': 'w',
                 'rule': ' 500',
                 'target': '.'}
        with self.assertRaises(ValidationError):
            self.processing.validate(arg2)

        arg3 = { 'src': '.',
                 'filterby': 'w',
                 'rule': 'GE 500',
                 'target': '.'}
        try:
            self.processing.validate(arg3)
        except ValidationError:
            self.fail('Exception raised')
