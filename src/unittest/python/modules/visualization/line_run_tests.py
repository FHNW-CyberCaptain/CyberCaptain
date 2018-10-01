import unittest, os, shutil

from cybercaptain.visualization.line import visualization_line

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_CHARTS_FOLDER = os.path.join(TESTDATA_FOLDER, 'chart_inputs')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

TESTDATA_SRC_FILENAME =  os.path.join(TESTDATA_CHARTS_FOLDER, 'input_data_10_counted-*.ccsf')
TESTDATA_SRC_FILENAME_SINGLE =  os.path.join(TESTDATA_CHARTS_FOLDER, 'input_data_10_counted-1.ccsf')

TESTDATA_TARGET_FILENAME_PNG =  os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'VisualizationLineRunOut.png')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class VisualizationLineRunTest(unittest.TestCase):
    """
    Test the visualization bar for the run method
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)
    
    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)
        
    def test_run(self):
        """
        Test if the visu line run method runs correct
        """
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedlineplot.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'rotateXTicks': 90,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedlineplot-rot.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'rotateXTicks': 90,
            'showGrid': True,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedlineplot-rotgrid.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'rotateXTicks': 90,
            'lineStyle': ':',
            'markerStyle': '*',
            'showGrid': True,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedlineplot-linemarker.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'rotateXTicks': 90,
            'lineStyle': ':',
            'markerStyle': '*',
            'threshold': 5,
            'showGrid': True,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedlineplot-thresh.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'rotateXTicks': 90,
            'lineStyle': ':',
            'markerStyle': '*',
            'threshold': 5,
            'showGrid': True,
            'colormap': 'rainbow',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedlineplot-colormap.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'comparedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'rotateXTicks': 90,
            'lineStyle': ':',
            'markerStyle': '*',
            'threshold': 5,
            'showGrid': True,
            'filenamesRegexExtract': '(\d)',
            'colormap': 'rainbow',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-comparedlineplot.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'comparedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'title': 'TestTitle',
            'ylabel': 'TestYLabel',
            'xlabel': 'TestXLabel',
            'rotateXTicks': 90,
            'lineStyle': ':',
            'markerStyle': '*',
            'threshold': 5,
            'showGrid': True,
            'filenamesRegexExtract': '(\d)',
            'colormap': 'rainbow',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run()) 
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-comparedlineplot-titleaxis.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'comparedlineplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'title': 'TestTitle',
            'ylabel': 'TestYLabel',
            'xlabel': 'TestXLabel',
            'rotateXTicks': 90,
            'lineStyle': ':',
            'markerStyle': '*',
            'threshold': 5,
            'showGrid': True,
            'figureSize': [10,10],
            'filenamesRegexExtract': '(\d)',
            'colormap': 'rainbow',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vl = visualization_line(**arguments)
        self.assertTrue(vl.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-comparedlineplot-figsize.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG