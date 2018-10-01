import unittest
import json

from cybercaptain.processing.classing import processing_classing

class ProcessingSimpleClassingTest(unittest.TestCase):
    """
    Test the processing classing. Without multimatch and no others class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'classBy': 'attribute',
                     'classes': ['w'],
                     'rules': ['test'],
                     'keepOthers': 'false',
                     'multiMatch': 'false',
                     'target': '.'}
        self.classing = processing_classing(**arguments)

    def test_correct_classing(self):
        """
        Test if the correct class is found.
        """
        record = json.loads('{"attribute":"test"}')
        self.assertEqual(['w'], self.classing.getClasses(record), 'Class must be "w"')

    def test_no_class(self):
        """
        Test if no others class is defined.
        """
        record = json.loads('{"attribute":"Nick"}')
        self.assertEqual([], self.classing.getClasses(record), 'Class must be empty')

class ProcessingClassingOthersTest(unittest.TestCase):
    """
    Test the classing with keepOthers flag set to true.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'classBy': 'attribute',
                     'classes': ['w'],
                     'rules': ['test'],
                     'keepOthers': 'true',
                     'multiMatch': 'false',
                     'target': '.'}
        self.classing = processing_classing(**arguments)

    def test_correct_classing(self):
        """
        Test if the correct class is found.
        """
        record = json.loads('{"attribute":"test"}')
        self.assertEqual(['w'], self.classing.getClasses(record), 'Class must be "w"')

    def test_others_classing(self):
        """
        Test if the others class will be defined.
        """
        record = json.loads('{"attribute":"Nick"}')
        self.assertEqual(["others"], self.classing.getClasses(record), 'Class must be "others"')

class ProcessingClassingMultiTest(unittest.TestCase):
    """
    Test the classing with multiMatch flag set to true.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'classBy': 'attribute',
                     'classes': ['a', 'b'],
                     'rules': ['[a-z]', '[a-z]'],
                     'keepOthers': 'false',
                     'multiMatch': 'true',
                     'target': '.'}
        self.classing = processing_classing(**arguments)

    def test_correct_classing(self):
        """
        Test if the correct classes are found.
        """
        record = json.loads('{"attribute":"a"}')
        self.assertEqual(['a', 'b'], self.classing.getClasses(record), 'Class must be "a" and "b"')

    def test_no_classing(self):
        """
        Test if the no class is defined.
        """
        record = json.loads('{"attribute" : "123"}')
        self.assertEqual([], self.classing.getClasses(record), 'Class must be empty')
