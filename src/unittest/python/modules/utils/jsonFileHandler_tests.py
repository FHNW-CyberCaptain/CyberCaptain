"""
Testing the File Handler
"""
import unittest
import os
import shutil
import json

from cybercaptain.utils.jsonFileHandler import json_file_reader, json_file_writer
from cybercaptain.utils.exceptions import LinePassedError, LineNotFoundError

TESTDATA_FOLDER = os.path.join(os.path.dirname(__file__), '../assets')
TESTDATA_GEN_OUTPUT_FOLDER = os.path.join(TESTDATA_FOLDER, '../output')
TESTDATA_SRC_FILENAME = os.path.join(TESTDATA_FOLDER, 'json_file_reader.json')
TESTDATA_TARGET_FILENAME = os.path.join(TESTDATA_GEN_OUTPUT_FOLDER, 'json_file_writer.json')

class FileReaderTest(unittest.TestCase):
    """
    Test the file reader class. The method ``close`` is not tested, as it depends on a python method.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.fr = json_file_reader(TESTDATA_SRC_FILENAME)

    def tearDown(self):
        self.fr.close()

    def test_reading_line(self):
        """
        Test if the line can be read.
        """
        self.assertFalse(self.fr.isEOF(), "File cannot be EOF, there are two lines in it!")
        record = self.fr.readRecord()
        true_record = json.loads('{"testInt" : 1,"testList" : [123,12] }')
        self.assertEqual(record, true_record, "The records are not equal!")

    def test_reading_line_by_number(self):
        """
        Test if the read line by number works.
        """
        record = self.fr.readLineRecord(2)
        true_record = json.loads('{"testInt" : 1,"testList" : [123,12] }')
        self.assertEqual(record, true_record)

    def test_reading_line_by_passed_number(self):
        """
        Test if the read line by number works.
        """
        self.fr.readRecord()
        with self.assertRaises(LinePassedError):
            self.fr.readLineRecord(1)

    def test_reading_line_by_number_not_found(self):
        """
        Test if the read line by number works.
        """
        with self.assertRaises(LineNotFoundError):
            self.fr.readLineRecord(3)

    def test_EOF(self):
        """
        Test if the EOF method works correctly
        """
        self.assertFalse(self.fr.isEOF(), "File cannot be EOF, there is are two lines in it!")
        self.fr.readRecord()
        self.fr.readRecord()
        self.assertTrue(self.fr.isEOF(), "File must be EOF, there are no more lines to be read!")

class FileWriterTest(unittest.TestCase):
    """
    Test the file writer class. The method ``close`` is not tested, as it depends on a python method.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        if not os.path.exists(TESTDATA_GEN_OUTPUT_FOLDER):
            os.makedirs(TESTDATA_GEN_OUTPUT_FOLDER)
        self.fw = json_file_writer(TESTDATA_TARGET_FILENAME)

    def tearDown(self):
        shutil.rmtree(TESTDATA_GEN_OUTPUT_FOLDER)

    def test_writing_line(self):
        """
        Testing the write line.
        """
        test_json = '{"test" : "Hello Nick"}'
        self.fw.writeRecord(test_json)
        with open(TESTDATA_TARGET_FILENAME+'.tmp','r') as f:
            the_file = f.read()

        self.assertEqual(the_file, '"{\\"test\\" : \\"Hello Nick\\"}"')
        self.fw.close()

    def test_renaming(self):
        """
        Testing if the file will be renamed.
        """
        self.fw.writeRecord('{"a" : 1}')
        self.fw.close()
        self.assertTrue(os.path.exists(TESTDATA_TARGET_FILENAME), "File must be found!")

    def test_abort(self):
        """
        Testing if the abort does not rename
        """
        self.fw.writeRecord('{"a" : 1}')
        self.fw.abort()
        self.assertTrue(os.path.exists(TESTDATA_TARGET_FILENAME+'.tmp'), "File must be found!")
