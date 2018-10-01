import unittest

from cybercaptain.visualization.line import visualization_line
from cybercaptain.utils.exceptions import ValidationError

class VisualizationLineTest(unittest.TestCase):
    """
    Test the visualization line chart validation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'type': '.',
                     'dataAttribute': '.',
                     'groupNameAttribute': '.',
                     'target': '.'}
        self.visualization = visualization_line(**arguments)

    def test_empty_arguments(self):
        """
        Tests if all the validation checks are triggered if needed.
        """
        arg = {'src': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg)

        arg = {'src': '.',
                'type': '.',
                'groupNameAttribute': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg)

        arg = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg)

        arg = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 'NOTINT',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg)

        arg = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'figureSize': 'NOTALIST',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg)

        arg = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'figureSize': [20,10,5],
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg)

        arg = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'rotateXTicks': 'NOTANINT',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg)

        arg = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'colormap': 'NOTEXISTINGCOLORMAP',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg)