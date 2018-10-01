import unittest, os

from cybercaptain.store.base import store_base
from cybercaptain.utils.exceptions import ValidationError

class StoreBaseTest(unittest.TestCase):
    """
    Test the store processing base
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {}
        self.store = store_base(**arguments)

    def test_base_class(self):
        # Test Base Run
        with self.assertRaises(NotImplementedError):
            self.store.run()

        # Test Base Validate
        with self.assertRaises(ValidationError):
            self.store.validate({"target":"xz"})
        with self.assertRaises(ValidationError):
            self.store.validate({"src":"xz"})
        with self.assertRaises(ValidationError):
            self.store.validate({"xy":"xz"})
        with self.assertRaises(ValidationError):
            self.store.validate({})