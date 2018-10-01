import unittest

from cybercaptain.visualization.bar import visualization_bar
from cybercaptain.utils.exceptions import ValidationError

class VisualizationBarTest(unittest.TestCase):
    """
    Test the visualization bar chart validation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = {'src': '.',
                     'type': '.',
                     'dataAttribute': '.',
                     'groupNameAttribute': '.',
                     'target': '.'}
        self.visualization = visualization_bar(**arguments)

    def test_empty_arguments(self):
        """
        Tests if all the validation checks are triggered if needed.
        """
        arg1 = {'src': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)

        arg2 = {'src': '.',
                'type': '.',
                'groupNameAttribute': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg2)

        arg3 = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg3)

        arg4 = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 'NOTINT',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg4)

        arg5 = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'figureSize': 'NOTALIST',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg5)

        arg6 = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'figureSize': [20,10,5],
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg6)

        arg7 = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'rotateXTicks': 'NOTANINT',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg7)

        arg8 = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'rotateYTicks': 'NOTANINT',
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg8)

        arg9 = {'src': '.',
                'type': '.',
                'dataAttribute': '.',
                'groupNameAttribute': '.',
                'threshold': 4,
                'colormap': 'NOTEXISTINGCOLORMAP',
                'rotateYTicks': 2,
                'target': '.'}

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg9)