import unittest, os, shutil
import argparse

from runCybercaptain import CyberCaptain, create_parser, main as ccMain
from configobj import ConfigObjError

from cybercaptain.utils.exceptions import ValidationError, ConfigurationError

TEST_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'assets/output')
TEST_INPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'assets')
TESTDATA_CONFIG_FOLDER = os.path.join(os.path.dirname(__file__), 'assets/configs')

TESTDATA_CONFIG_SCRIPT_VALID = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_valid.ccs')
TESTDATA_CONFIG_SCRIPT_VALID_NOWC = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_valid_no_wildcards.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_SECTIONS = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_sections.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_MODULES = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_modules.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_NAME = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_name.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_PROJECTROOT = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_projectroot.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_ROOTCONFIG = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_rootconfs.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_DUPTRGT = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_dup_targets.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_IDENT = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_identifier.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_REST_TRGT = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_restricted_trgt.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_WC_NCREATED = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_wildcard_ncreated.ccs')
TESTDATA_CONFIG_SCRIPT_VALID_OVERWRITTING = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_valid_overwrittings.ccs')
TESTDATA_CONFIG_SCRIPT_VALID_WC = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_valid_wc_test.ccs')
TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_valid_testrun.ccs')
TESTDATA_CONFIG_SCRIPT_NVALID_TRGTNOTUSED = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_not_valid_target_notused.ccs')

# Checksum Check Tests - Check if canceled after the config has changed (same projectName -> same KVStore -> checksum should match)
TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED = os.path.join(TESTDATA_CONFIG_FOLDER, 'script_valid_testrun_changed.ccs')

TESTDATA_CONFIG_MODULES_VALID = os.path.join(TESTDATA_CONFIG_FOLDER, 'modules_valid.ccc')
TESTDATA_CONFIG_MODULES_NVALID = os.path.join(TESTDATA_CONFIG_FOLDER, 'modules_not_valid.ccc')
TESTDATA_CONFIG_MODULES_MISSES = os.path.join(TESTDATA_CONFIG_FOLDER, 'modules_valid_misses.ccc')
TESTDATA_CONFIG_MODULES_MISS_MODULES = os.path.join(TESTDATA_CONFIG_FOLDER, 'modules_valid_missing_modules.ccc')

class CyberCaptainRunTest(unittest.TestCase):
    """
    Test the cybercaptain main run class. Class is responsible for running the project.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp_output_folder(self):
        if not os.path.exists(TEST_OUTPUT_FOLDER):
            os.makedirs(TEST_OUTPUT_FOLDER)

    def tearDown_output_folder(self):
        shutil.rmtree(TEST_OUTPUT_FOLDER)

    def setUp(self):
        self.parser = create_parser()
        if not os.path.exists(TEST_OUTPUT_FOLDER):
            os.makedirs(TEST_OUTPUT_FOLDER)
    
    def tearDown(self):
        shutil.rmtree(TEST_OUTPUT_FOLDER)

    def test_cc_init_method(self):
        # Test For Not Existing Script Config File
        with self.assertRaises(FileNotFoundError):
            CyberCaptain("NOTEXISTINGCONFIG.ccs", TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # Test For Not Existing Modules Config File
        with self.assertRaises(FileNotFoundError):
            CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID, "NOTEXISTINGMODULECONF.ccc", True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # Test For Not Unique Sections Should Fail To Parse The File
        with self.assertRaises(ConfigObjError):
            CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_SECTIONS, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # Test For Not Valid Modules Config
        with self.assertRaises(ConfigObjError):
            CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID, TESTDATA_CONFIG_MODULES_NVALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # Test For No Defined Placeholders But Placeholders In Config
        with self.assertRaises(KeyError):
            CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID, TESTDATA_CONFIG_MODULES_VALID, True, {}, False)

        # Test For Wrong Defined Placeholders With Placeholders In Config
        with self.assertRaises(KeyError):
            CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID, TESTDATA_CONFIG_MODULES_VALID, True, {"WRONG":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

    def test_cc_valid_config_method(self):
        # Script Config Not A Valid Name
        with self.assertRaises(KeyError):
            cc1 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_NAME, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

         # Script Config Not A Project Root
        with self.assertRaises(KeyError):
            cc1 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_PROJECTROOT, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # Script Config Module Contains A Reserved Root Config Attribute
        with self.assertRaises(ConfigurationError):
            cc1 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_ROOTCONFIG, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)
            
        # Modules Config Does Not Contain The wildcard_src_modules key or/and restricted_target_modules key
        cc2 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_NOWC, TESTDATA_CONFIG_MODULES_MISSES, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)
        self.assertEquals(cc2.loaded_modules_conf["wildcard_src_modules"],[])
        self.assertEquals(cc2.loaded_modules_conf["restricted_target_modules"],[])

        # Script Config Does Contain Wildcards But Module Not in modules config wildcard_src_modules
        with self.assertRaises(ConfigurationError):
            cc3 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID, TESTDATA_CONFIG_MODULES_MISSES, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # Script Config Does Contain Duplicated Targets (Which would overwrite files)
        with self.assertRaises(ConfigurationError):
            cc4 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_DUPTRGT, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)
        
        # Script Config Does Contain A Block Without A Module Name Or Without Unique Identifier
        with self.assertRaises(ConfigurationError):
            cc5 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_IDENT, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)
        
        # Script Config Does Contain A Module Which Is Not Defined In The Modules Config
        with self.assertRaises(ConfigurationError):
            cc6 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID, TESTDATA_CONFIG_MODULES_MISS_MODULES, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # Script Config Does Contain A Module Which Is Using A Restricted Module Target As A Source
        # Restricted modules cannot be used as a source anywhere as they represent a final step which cannot be used further
        with self.assertRaises(ConfigurationError):
            cc7 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_REST_TRGT, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        #  Script Config Does Contain A WildCard Source But Source Will Never Be Created As A Target Anywhere
        with self.assertRaises(ConfigurationError):
            cc8 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_WC_NCREATED, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # File already existing and also in targets so will be overwritten, warning will be shown
        cc9 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_OVERWRITTING, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

        # Wildcard Source And In Target
        cc10 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_WC, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)

    def test_cc_run_config_method(self):
        # Needs custom placeholder {test_output_path} to set the output path to clean up after & test_input_path for input file

        # Run First Run
        self.tearDown_output_folder()
        self.setUp_output_folder()
        cc_run = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN, TESTDATA_CONFIG_MODULES_VALID, False, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER, "test_input_path": TEST_INPUT_FOLDER}, False)

        # Should skip steps as second run with same params
        cc_run2 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN, TESTDATA_CONFIG_MODULES_VALID, False, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER, "test_input_path": TEST_INPUT_FOLDER}, False)

        # Test checksum check - config has changed but same projectName given (so its a risk for eg. the kv store) -> Stop
        with self.assertRaises(ConfigurationError):
            cc_run3 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED, TESTDATA_CONFIG_MODULES_VALID, False, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER, "test_input_path": TEST_INPUT_FOLDER}, False)

        # Run With --ignorechecksum flag to still run although CCS changed
        cc_run4 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED, TESTDATA_CONFIG_MODULES_VALID, False, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER, "test_input_path": TEST_INPUT_FOLDER}, False, True)


    def test_cc_main_method(self):
        # No config file defined
        with self.assertRaises(Exception):
            cc_main = ccMain(self.parser.parse_args(['-v']))

        # Not existing script config file
        with self.assertRaises(FileNotFoundError):
            cc_main2 = ccMain(self.parser.parse_args(['-c','conf.ccs', '-v']))

        # Not existing modules config file
        with self.assertRaises(FileNotFoundError):
            cc_main3 = ccMain(self.parser.parse_args(['-c', TESTDATA_CONFIG_SCRIPT_VALID, '-mc', 'TEST_MODULE_CONF_LOC.ccc','-cp','count=1','-cp','test_output_path='+TEST_OUTPUT_FOLDER,'-v']))
        
        # Undefined Placeholders
        with self.assertRaises(KeyError):
            cc_main4 = ccMain(self.parser.parse_args(['-c', TESTDATA_CONFIG_SCRIPT_VALID, '-mc', TESTDATA_CONFIG_MODULES_VALID,'-v']))
        
        cc_main5 = ccMain(self.parser.parse_args(['-c', TESTDATA_CONFIG_SCRIPT_VALID, '-mc', TESTDATA_CONFIG_MODULES_VALID,'-cp','count=1','-cp','test_output_path='+TEST_OUTPUT_FOLDER,'-v']))
        self.assertEqual(cc_main5.modulesConfig, TESTDATA_CONFIG_MODULES_VALID)


    def test_cc_is_wc_src_module_method(self):
        cc11 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_WC, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)
        self.assertEquals(cc11.is_wc_src_module("visualization_bar TESTNAME",cc11.loaded_modules_conf), True)
        self.assertEquals(cc11.is_wc_src_module("XZY TESTNAME",cc11.loaded_modules_conf), False)

    def test_cc_get_final_steps_method(self):
        cc12 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_WC, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)
        self.assertEquals(cc12.get_final_steps(cc12.loaded_conf, cc12.loaded_modules_conf), ['visualization_bar LOCAL_BAR1'])

        # Added to test for the false case in the target_used_as_wc_src method
        # target_used_as_wc_src = false means: the checked target is not used anywhere as a src (with wildcard) anyomer -> final step
        cc14 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_NVALID_TRGTNOTUSED, TESTDATA_CONFIG_MODULES_VALID,True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)
        self.assertEquals(cc12.get_final_steps(cc14.loaded_conf, cc14.loaded_modules_conf), ['store_local LOCAL_STORE2', 'visualization_bar LOCAL_BAR1'])

    def test_cc_get_config_name_for_attribute_method(self):
        cc13 = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_WC, TESTDATA_CONFIG_MODULES_VALID, True, {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER}, False)
        self.assertEquals(cc13.get_config_name_for_attribute(cc13.loaded_conf, "src", os.path.join(TEST_OUTPUT_FOLDER, "ssh_local_filter_openssh_1.cctf"), False), 'processing_group LOCAL_GROUP1')
        self.assertEquals(cc13.get_config_name_for_attribute(cc13.loaded_conf, "target", os.path.join(TEST_OUTPUT_FOLDER, "mvp_final_*.cctf"), True), 'processing_group LOCAL_GROUP1')
        self.assertEquals(cc13.get_config_name_for_attribute(cc13.loaded_conf, "src", "xz", False), None)

    def test_cc_checksum_check_method(self):
        self.tearDown_output_folder()
        self.setUp_output_folder()
        # 'First Run' - Checksum new written to KV store
        cc_checksum_check = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED, TESTDATA_CONFIG_MODULES_VALID, False, 
            {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER, "test_input_path": TEST_INPUT_FOLDER}, False, False, False)
        self.assertEquals(cc_checksum_check.checksum_check("TEST_CHECKSUM", TEST_OUTPUT_FOLDER, TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN), True)

        # 'Second Run' - Script config changed -> Return False
        self.assertEquals(cc_checksum_check.checksum_check("TEST_CHECKSUM", TEST_OUTPUT_FOLDER, TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED), False)

        # 'Third run' - Ignorechecksum flag set -> Continue
        cc_checksum_check = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED, TESTDATA_CONFIG_MODULES_VALID, False,
            {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER, "test_input_path": TEST_INPUT_FOLDER}, False, False, True)
        self.assertEquals(cc_checksum_check.checksum_check("TEST_CHECKSUM", TEST_OUTPUT_FOLDER, TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED), True)

        # 'Fourth run' - Overwritechecksum flag set -> Return True As The Checksum Is Updated
        cc_checksum_check = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED, TESTDATA_CONFIG_MODULES_VALID, False,
            {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER, "test_input_path": TEST_INPUT_FOLDER}, False, True, False)
        self.assertEquals(cc_checksum_check.checksum_check("TEST_CHECKSUM", TEST_OUTPUT_FOLDER, TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED), True)

        # 'Fifth run' - Checksum was updated so still the same (No ignore & no overwrite flag) -> Return True
        cc_checksum_check = CyberCaptain(TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED, TESTDATA_CONFIG_MODULES_VALID, False,
            {"count":"1", "test_output_path": TEST_OUTPUT_FOLDER, "test_input_path": TEST_INPUT_FOLDER}, False, False, False)
        self.assertEquals(cc_checksum_check.checksum_check("TEST_CHECKSUM", TEST_OUTPUT_FOLDER, TESTDATA_CONFIG_SCRIPT_VALID_TESTRUN_CHANGED), True)