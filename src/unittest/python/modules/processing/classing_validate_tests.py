import unittest

from cybercaptain.processing.classing import processing_classing
from cybercaptain.utils.exceptions import ValidationError

class ProcessingClassingValidateTest(unittest.TestCase):
    """
    Test the processing classing validation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'classBy': '.',
                     'classes': ['.'],
                     'rules': ['.'],
                     'keepOthers': '.',
                     'multiMatch': '.',
                     'target': '.'}
        self.classing = processing_classing(**arguments)

    def test_empty_arguments(self):
        """
        Test if any not given argument raises an exception
        """
        arg = {'classBy': '.',
               'classes': ['.'],
               'rules': ['.'],
               'keepOthers': '.',
               'multiMatch': '.',
               'target': '.'}

        with self.assertRaises(ValidationError):
            self.classing.validate(arg)

        arg = {'src': '.',
               'classes': ['.'],
               'rules': ['.'],
               'keepOthers': '.',
               'multiMatch': '.',
               'target': '.'}

        with self.assertRaises(ValidationError):
            self.classing.validate(arg)

        arg = {'src': '.',
               'classBy': ['.'],
               'rules': ['.'],
               'keepOthers': '.',
               'multiMatch': '.',
               'target': '.'}

        with self.assertRaises(ValidationError):
            self.classing.validate(arg)

        arg = {'src': '.',
               'classBy': ['.'],
               'classes': ['.'],
               'keepOthers': '.',
               'multiMatch': '.',
               'target': '.'}

        with self.assertRaises(ValidationError):
            self.classing.validate(arg)

        arg = {'src': '.',
               'classBy': ['.'],
               'classes': ['.'],
               'rules': '.',
               'multiMatch': '.',
               'target': '.'}

        with self.assertRaises(ValidationError):
            self.classing.validate(arg)

        arg = {'src': '.',
               'classBy': ['.'],
               'classes': ['.'],
               'rules': '.',
               'keepOthers': '.',
               'target': '.'}

        with self.assertRaises(ValidationError):
            self.classing.validate(arg)

        arg = {'src': '.',
               'classBy': ['.'],
               'classes': ['.'],
               'rules': '.',
               'keepOthers': '.',
               'multiMatch': '.'}

        with self.assertRaises(ValidationError):
            self.classing.validate(arg)

    def test_same_length_attribute(self):
        """
        Test if the validation checks the length of classes and rules.
        """
        arg = {'src': '.',
               'classBy': '.',
               'classes': ['.', '.'],
               'rules': ['.'],
               'keepOthers': '.',
               'multiMatch': '.',
               'target': '.'}
        
        with self.assertRaises(ValidationError):
            self.classing.validate(arg)

        arg = {'src': '.',
               'classBy': '.',
               'classes': ['.'],
               'rules': ['.', '.'],
               'keepOthers': '.',
               'multiMatch': '.',
               'target': '.'}
        
        with self.assertRaises(ValidationError):
            self.classing.validate(arg)
