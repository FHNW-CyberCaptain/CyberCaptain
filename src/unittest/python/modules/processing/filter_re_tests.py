import unittest

from cybercaptain.processing.filter import processing_filter

class ProcessingFilterRETest(unittest.TestCase):
    """
    Test the filters for RE
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'filterby': 'regular expression',
                     'rule': 'RE aa$', # the content must end on two as'.
                     'target': '.'}
        self.processing = processing_filter(**arguments)

    def test_re_positive(self):
        """
        Test if the filter passes RE correctly.
        """
        # border line test
        self.assertTrue(self.processing.filter({"regular expression":"aa"}), 'should not be filtered')
        # deep test
        self.assertTrue(self.processing.filter({"regular expression":"baa"}), 'should not be filtered')

    def test_re_negative(self):
        """
        Test if the filter fails RE correctly.
        """
        # border line test
        self.assertFalse(self.processing.filter({"regular expression":"bab"}), 'should be filtered')
        # deep test
        self.assertFalse(self.processing.filter({"regular expression":"aab"}), 'should be filtered')
