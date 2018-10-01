import unittest

from cybercaptain.processing.filter import processing_filter

class ProcessingFilterEQTest(unittest.TestCase):
    """
    Test the filters for EQ
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'filterby': 'EQ',
                     'rule': 'EQ 500', # the content must end on two as'.
                     'target': '.'}
        self.processing = processing_filter(**arguments)

    def test_eq_positive(self):
        """
        Test if the filter passes EQ correctly.
        """
        # border line test
        self.assertTrue(self.processing.filter({"EQ":500}), 'should not be filtered')

    def test_eq_negative(self):
        """
        Test if the filter fails EQ correctly.
        """
        # border line test
        self.assertFalse(self.processing.filter({"EQ":501}), 'should be filtered')
        self.assertFalse(self.processing.filter({"EQ":499}), 'should be filtered')
        # deep test
        self.assertFalse(self.processing.filter({"EQ":600}), 'should be filtered')
        self.assertFalse(self.processing.filter({"EQ":400}), 'should be filtered')
