import unittest

from cybercaptain.processing.filter import processing_filter

class ProcessingFilterLETest(unittest.TestCase):
    """
    Test the filters for LE
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'filterby': 'LE',
                     'rule': 'LE 500',
                     'target': '.'}
        self.processing = processing_filter(**arguments)

    def test_le_positive(self):
        """
        Test if the filter passes LE correctly.
        """
        # border line test
        self.assertTrue(self.processing.filter({"LE":500}), 'should not be filtered')
        # deep test
        self.assertTrue(self.processing.filter({"LE":400}), 'should not be filtered')

    def test_le_negative(self):
        """
        Test if the filter fails LE correctly.
        """
        # border line test
        self.assertFalse(self.processing.filter({"LE":501}), 'should be filtered')
        # deep test
        self.assertFalse(self.processing.filter({"LE":600}), 'should be filtered')
