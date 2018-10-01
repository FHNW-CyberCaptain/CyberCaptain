import unittest, os

from cybercaptain.processing.base import processing_base
from cybercaptain.utils.exceptions import ValidationError

class ProcessingBaseTest(unittest.TestCase):
    """
    Test the data processing base
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {}
        self.processing = processing_base(**arguments)

    def test_base_class(self):
        # Test Base Run
        with self.assertRaises(NotImplementedError):
            self.processing.run()

        # Test Base Validate
        with self.assertRaises(ValidationError):
            self.processing.validate({"target":"xz"})
        with self.assertRaises(ValidationError):
            self.processing.validate({"src":"xz"})
        with self.assertRaises(ValidationError):
            self.processing.validate({"xy":"xz"})
        with self.assertRaises(ValidationError):
            self.processing.validate({})