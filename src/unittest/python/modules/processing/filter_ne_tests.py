import unittest

from cybercaptain.processing.filter import processing_filter

class ProcessingFilterNETest(unittest.TestCase):
    """
    Test the filters for NE
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'filterby': 'NE',
                     'rule': 'NE 500', # the content must end on two as'.
                     'target': '.'}
        self.processing = processing_filter(**arguments)

    def test_ne_positive(self):
        """
        Test if the filter passes NE correctly.
        """
        # border line test
        self.assertTrue(self.processing.filter({"NE":501}), 'should not be filtered')
        self.assertTrue(self.processing.filter({"NE":499}), 'should not be filtered')

        #deep test
        self.assertTrue(self.processing.filter({"NE":600}), 'should not be filtered')
        self.assertTrue(self.processing.filter({"NE":400}), 'should not be filtered')
        

    def test_ne_negative(self):
        """
        Test if the filter fails NE correctly.
        """
        # border line test
        self.assertFalse(self.processing.filter({"NE":500}), 'should be filtered')
