import unittest, os, shutil

from cybercaptain.visualization.bar import visualization_bar

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_CHARTS_FOLDER = os.path.join(TESTDATA_FOLDER, 'chart_inputs')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'output')

TESTDATA_SRC_FILENAME =  os.path.join(TESTDATA_CHARTS_FOLDER, 'input_data_10_counted-*.ccsf')
TESTDATA_SRC_FILENAME_SINGLE =  os.path.join(TESTDATA_CHARTS_FOLDER, 'input_data_10_counted-1.ccsf')

TESTDATA_TARGET_FILENAME_PNG = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'VisualizationBarRunOut.png')
TESTDATA_TARGET_FILENAME_SVG = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'VisualizationBarRunOut.svg')

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot': TESTDATA_FOLDER, 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class VisualizationBarRunTest(unittest.TestCase):
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
        Test if the visu bar run method runs correct
        """
        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedbarplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedbarplot.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedbarplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedbarplot_threshold.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'groupedbarplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'title': 'Unittest title',
            'xlabel': 'Unittest xlabel',
            'ylabel': 'Unittest ylabel',
            'threshold': 5,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedbarplot_threshold_lbl.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME_SINGLE,
            'type': 'groupedbarplot',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-groupedbarplot_single.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'histogram',
            'dataAttribute': 'grouped_value',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-histogram.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME_SINGLE,
            'type': 'histogram',
            'dataAttribute': 'grouped_value',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-histogram_single.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplot3d',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplot3d.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplot3d',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplot3d_thresh.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplot3d',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'colormapAscending': True,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplot3d_ascheat.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplotgroupedstacked',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplotgroupedstacked.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG


        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplotgroupedstacked',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplotgroupedstacked_thresh.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplotcomparedstacked',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplotcomparedstacked.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplotcomparedstacked',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplotcomparedstacked_thresh.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplotcomparedstacked',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'figureSize': [10,10],
            'filenamesRegexExtract': '([-+]\\d+)',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplotcomparedstacked_thresh_rg.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplotcomparedstacked',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'figureSize': [10,10],
            'horizontal': True,
            'filenamesRegexExtract': '([-+]\\d+)',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplotcomparedstacked_horiz.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplotcomparedstacked',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'figureSize': [10,10],
            'horizontal': True,
            'scaledTo100': True,
            'filenamesRegexExtract': '([-+]\\d+)',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplotcomparedstacked_horiz_100.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG

        arguments = append_needed_args({'src': TESTDATA_SRC_FILENAME,
            'type': 'barplotgroupedstacked',
            'dataAttribute': 'grouped_value',
            'groupNameAttribute': 'group_name',
            'threshold': 5,
            'figureSize': [10,10],
            'horizontal': True,
            'scaledTo100': True,
            'filenamesRegexExtract': '([-+]\\d+)',
            'target': TESTDATA_TARGET_FILENAME_PNG})
        vb = visualization_bar(**arguments)
        self.assertTrue(vb.run())
        self.assertTrue(os.path.isfile(TESTDATA_TARGET_FILENAME_PNG))
        #self.assertTrue(open(TESTDATA_FOLDER+"/test-barplotgroupedstacked_horiz_100.png","rb").read() == open(TESTDATA_TARGET_FILENAME_PNG,"rb").read()) #Compare PNG