"""
Testing the File Handler
"""
import unittest
import os
import shutil

from cybercaptain.utils.csvFileHandler import csv_file_writer

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, 'CSV_output')
TESTDATA_TARGET_FILENAME = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'csv_file_writer.csv')

class FileWriterTest(unittest.TestCase):
    """
    Test the file writer class. The method ``close`` is not tested, as it depends on a python method.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)

    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_writing_line(self):
        """
        Testing the write line.
        """
        file_header = ['firstName', 'lastName']
        fw = csv_file_writer(TESTDATA_TARGET_FILENAME, file_header)
        test_dict = {'firstName' : 'Edward', 'lastName' : 'Thatch'}
        fw.writeCSVRow(test_dict)
        fw.close()

        with open(TESTDATA_TARGET_FILENAME, 'r') as f:
            the_file = f.read()

        self.assertMultiLineEqual(the_file, '"firstName","lastName"\n"Edward","Thatch"\n')

    def test_renaming(self):
        """
        Testing if the file will be renamed.
        """
        fw = csv_file_writer(TESTDATA_TARGET_FILENAME, ['a'])
        fw.writeCSVRow({"a" : 1})
        fw.close()
        self.assertTrue(os.path.exists(TESTDATA_TARGET_FILENAME), "File must be found!")

    def test_abort(self):
        """
        Testing if the abort does not rename
        """
        fw = csv_file_writer(TESTDATA_TARGET_FILENAME, ['a'])
        fw.writeCSVRow({"a" : 1})
        fw.abort()
        self.assertTrue(os.path.exists(TESTDATA_TARGET_FILENAME+'.tmp'), "File must be found!")
