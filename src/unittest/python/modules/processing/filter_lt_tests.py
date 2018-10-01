import unittest

from cybercaptain.processing.filter import processing_filter

class ProcessingFilterLTTest(unittest.TestCase):
    """
    Test the filters for LT
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'filterby': 'LT',
                     'rule': 'LT 500',
                     'target': '.'}
        self.processing = processing_filter(**arguments)

    def test_LT_positive(self):
        """
        Test if the filter passes LT correctly.
        """
        # border line test
        self.assertTrue(self.processing.filter({"LT":499}), 'should not be filtered')
        # deep test
        self.assertTrue(self.processing.filter({"LT":400}), 'should not be filtered')

    def test_LT_negative(self):
        """
        Test if the filter fails LT correctly.
        """
        # border line test
        self.assertFalse(self.processing.filter({"LT":500}), 'should be filtered')
        # deep test
        self.assertFalse(self.processing.filter({"LT":600}), 'should be filtered')
