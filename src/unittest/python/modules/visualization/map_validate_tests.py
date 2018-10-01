import unittest
import os, shutil

from cybercaptain.visualization.map import visualization_map
from cybercaptain.utils.exceptions import ValidationError


TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class DataVisualizationMapValidateTest(unittest.TestCase):
    """
    Test the visualization map chart png validation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        arguments = append_needed_args({'src': '.',
                    'map' : 'world',
                    'type' : '.',
                    'colormap' : '.',
                    'countryCodeAttribute' : '.',
                    'groupedValueAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : '.',
                    'target': '.'})
        self.visualization = visualization_map(**arguments)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)
    
    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_validation_heatmap(self):
        """
        Testing the heatmap validation.
        """

        # SRC missing
        arg1 = append_needed_args({
                    'map' : 'world',
                    'type' : 'viridis',
                    'colormap' : '.',
                    'countryCodeAttribute' : '.',
                    'groupedValueAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : '.',
                    'target': '.'})

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)

        # map missing
        arg1 = append_needed_args({'src': '.',
                    'type' : '.',
                    'colormap' : 'viridis',
                    'countryCodeAttribute' : '.',
                    'groupedValueAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : '.',
                    'target': '.'})

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)

        # type missing
        arg1 = append_needed_args({'src': '.',
                    'map' : 'world',
                    'colormap' : 'viridis',
                    'countryCodeAttribute' : '.',
                    'groupedValueAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : '.',
                    'target': '.'})

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)

        # colormap missing
        arg1 = append_needed_args({'src': '.',
                    'map' : 'world',
                    'countryCodeAttribute' : '.',
                    'groupedValueAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : '.',
                    'target': '.'})

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)

        # colormap not existing
        arg1 = append_needed_args({'src': '.',
                    'map' : 'world',
                    'colormap' : 'NOTEXISTINGCOLOR',
                    'countryCodeAttribute' : '.',
                    'groupedValueAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : '.',
                    'target': '.'})

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)

        # Heatmap: countryCodeAttribute missing
        arg1 = append_needed_args({'src': '.',
                    'map' : 'world',
                    'type' : 'heatmap',
                    'colormap' : 'viridis',
                    'groupedValueAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : '.',
                    'target': '.'})

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)

        # Heatmap: groupedValueAttribute missing
        arg1 = append_needed_args({'src': '.',
                    'map' : 'world',
                    'type' : 'heatmap',
                    'colormap' : 'viridis',
                    'countryCodeAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : '.',
                    'target': '.'})

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)

        # Heatmap: threshold not int
        arg1 = append_needed_args({'src': '.',
                    'map' : 'world',
                    'type' : 'heatmap',
                    'colormap' : 'viridis',
                    'countryCodeAttribute' : '.',
                    'groupedValueAttribute' : '.',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 'not int',
                    'title' : '.',
                    'target': '.'})

        with self.assertRaises(ValidationError):
            self.visualization.validate(arg1)