import unittest, os

from cybercaptain.visualization.base import visualization_base
from cybercaptain.utils.exceptions import ValidationError

class VisualizationBaseTest(unittest.TestCase):
    """
    Test the data visualization base
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {}
        self.visualization = visualization_base(**arguments)

    def test_base_class(self):
        # Test Base Run
        with self.assertRaises(NotImplementedError):
            self.visualization.run()

        # Test Base Validate
        with self.assertRaises(ValidationError):
            self.visualization.validate({"target":"xz"})
        with self.assertRaises(ValidationError):
            self.visualization.validate({"src":"xz"})
        with self.assertRaises(ValidationError):
            self.visualization.validate({"xy":"xz"})
        with self.assertRaises(ValidationError):
            self.visualization.validate({})