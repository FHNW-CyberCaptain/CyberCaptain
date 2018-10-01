import unittest
import os, shutil

from cybercaptain.visualization.map import visualization_map

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class DataVisualizationMapTest(unittest.TestCase):
    """
    Test the visualization map chart png plotting.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)
    
    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_run_plotting_heatmap(self):
        """
        Testing weather the png heatmap is generated or not.
        """

        # Alpha 3 Country Codes
        target_file_name = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'test_png_plotting_heatmap_1.png')
        arguments = append_needed_args({'src': os.path.join(TESTDATA_FOLDER, 'test_plotting_heatmap_alpha3.cctf'),
                    'map' : 'world',
                    'type' : 'heatmap',
                    'colormap' : 'viridis_r',
                    'countryCodeAttribute' : 'country_code',
                    'groupedValueAttribute' : 'grouped_value',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : 'Unit Test',
                    'target': target_file_name})
        v_map = visualization_map(**arguments)
        v_map.geojson_map = os.path.join(TESTDATA_FOLDER, 'test.geojson')

        self.assertTrue(v_map.run())
        self.assertTrue(os.path.isfile(target_file_name))
        #elf.assertTrue(open(TESTDATA_FOLDER+"/test_png_plotting_heatmap_1.png","rb").read() == open(target_file_name,"rb").read()) #Compare PNG

        # Alpha 2 Country Codes Should Receive Same Plot As Its Converted
        target_file_name = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'test_png_plotting_heatmap_2.png')
        arguments = append_needed_args({'src': os.path.join(TESTDATA_FOLDER, 'test_plotting_heatmap_alpha2.cctf'),
                    'map' : 'world',
                    'type' : 'heatmap',
                    'colormap' : 'viridis_r',
                    'countryCodeAttribute' : 'country_code',
                    'groupedValueAttribute' : 'grouped_value',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : 'Unit Test',
                    'target': target_file_name})
        v_map = visualization_map(**arguments)
        v_map.geojson_map = os.path.join(TESTDATA_FOLDER, 'test.geojson')

        self.assertTrue(v_map.run())
        self.assertTrue(os.path.isfile(target_file_name))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test_png_plotting_heatmap_2.png","rb").read() == open(target_file_name,"rb").read()) #Compare PNG

        # Wrong Country Codes (Not Alpha2 & Not Alpha3)
        target_file_name = os.path.join(TESTDATA_FOLDER, 'test_png_plotting_heatmap_3.png')
        arguments = append_needed_args({'src': os.path.join(TESTDATA_FOLDER, 'test_plotting_heatmap_invalid_countrycode.cctf'),
                    'map' : 'world',
                    'type' : 'heatmap',
                    'colormap' : 'viridis_r',
                    'countryCodeAttribute' : 'country_code',
                    'groupedValueAttribute' : 'grouped_value',
                    'displayLegend' : 'yes',
                    'displayLabels' : 'yes',
                    'labelsThreshold' : 1,
                    'title' : 'Unit Test',
                    'target': target_file_name})
        v_map = visualization_map(**arguments)
        v_map.geojson_map = os.path.join(TESTDATA_FOLDER, 'test.geojson')

        self.assertFalse(v_map.run())
        self.assertFalse(os.path.isfile(target_file_name))
