import unittest, json

from cybercaptain.processing.clean import processing_clean

class ProcessingCleanKeepTest(unittest.TestCase):
    """
    Test the processing clean for keep
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'format': '.',
                     'keep': ['w','t.tn'],
                     'target': '.'}
        self.processing = processing_clean(**arguments)

    def test_keep(self):
        """
        Test if the cleaner cleans with keep successfully
        """
        self.assertEqual(self.processing.clean_json({"w":500,"t":{"tn":"1"}}), (True, {"w":500,"t":{"tn":"1"}}))
        self.assertEqual(self.processing.clean_json({"w":500,"t":{"tn":"1","p":1}}), (True, {"w":500,"t":{"tn":"1"}}))
        self.assertEqual(self.processing.clean_json({"w":500,"t":{"tn":"1","p":1},"k":"d"}), (True, {"w":500,"t":{"tn":"1"}}))

        # Test with attribute not existing
        with self.assertRaises(Exception):
            self.processing.clean_json({"w_renamed":500,"t":{"tn":"1"}})

        with self.assertRaises(Exception):
            self.processing.clean_json({"w":500,"t":{"tn_renamed":"1"}})

        arg1 = {'src': '.',
                     'format': '.',
                     'keep': ['w','t.lel'],
                     'ignoreMissingKeys': "true",
                     'target': '.'}
        self.processing = processing_clean(**arg1)
        self.assertEqual(self.processing.clean_json({"w_renamed":500,"t":{"tn":"1"}}), (True, {"t":{}}))

        arg2 = {'src': '.',
                'format': '.',
                'keep': ['w','t.tn'],
                'removeMissingKeys': "true",
                'target': '.'}
        self.processing = processing_clean(**arg2)
        self.assertEqual(self.processing.clean_json({"w_renamed":500,"t":{"tn":"1"}}), (False, {}))





        