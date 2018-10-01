import unittest

from cybercaptain.processing.filter import processing_filter

class ProcessingFilterGTTest(unittest.TestCase):
    """
    Test the filters for GT
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'filterby': 'w',
                     'rule': 'GT 500',
                     'target': '.'}
        self.processing = processing_filter(**arguments)

    def test_gt_positive(self):
        """
        Test if the filter passes GT correctly.
        """
        # border line test
        self.assertTrue(self.processing.filter({"w":501}), 'should not be filtered')
        # deep test
        self.assertTrue(self.processing.filter({"w":600}), 'should not be filtered')

    def test_gt_negative(self):
        """
        Test if the filter fails GT correctly.
        """
        # border line test
        self.assertFalse(self.processing.filter({"w":500}), 'should be filtered')
        # deep test
        self.assertFalse(self.processing.filter({"w":400}), 'should be filtered')
