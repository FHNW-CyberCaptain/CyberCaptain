import unittest

from cybercaptain.processing.filter import processing_filter

class ProcessingFilterGETest(unittest.TestCase):
    """
    Test the filters for GE
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'filterby': 'w',
                     'rule': 'GE 500',
                     'target': '.'}
        self.processing = processing_filter(**arguments)

    def test_ge_positive(self):
        """
        Test if the filter passes GE correctly.
        """
        # border line test
        self.assertTrue(self.processing.filter({"w":500}), 'should not be filtered')
        # deep test
        self.assertTrue(self.processing.filter({"w":600}), 'should not be filtered')

    def test_ge_negative(self):
        """
        Test if the filter fails GE correctly.
        """
        # border line test
        self.assertFalse(self.processing.filter({"w":499}), 'should be filtered')
        # deep test
        self.assertFalse(self.processing.filter({"w":400}), 'should be filtered')
