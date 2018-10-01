"""
This util module handles all the JSON files for the CyberCaptain modules.
"""
import json
import logging
import shutil
from cybercaptain.utils.exceptions import LinePassedError, LineNotFoundError

class json_file_reader():
    """
    The reader class allows to pass a file and path to read the file line by line and passes it back as a JSON object.

    **Parameters**:
		file_name : str
            The file location and name relative from call location.
    """
    def __init__(self, file_name):
        self.logger = logging.getLogger("CyberCaptain")
        self.line_pointer = open(file_name, "r")
        self.logger.debug("Opening file %s", file_name)
        self.next_line = self.line_pointer.readline()
        self.logger.debug("File %s is opened and ready to read from!", file_name)
        self.read_lines = 1
        self.current_line = 1
        self.logger.debug("Read line #%i", self.read_lines)
        self.file_name = file_name

    def readRecord(self):
        """
        Reades one line from the file and returns it as a JSON Object.

		**Returns**:
			The next line as a JSON object. Or null if the file has reached its end.
        """
        if self.isEOF():
            self.logger.warning("EOF! Maybe check your implementation!")
            return None
        json_obj = json.loads(self.next_line) # save the to be passed line
        self.next_line = self.line_pointer.readline() # read next line for the next call
        self.read_lines += 1
        self.current_line += 1
        #self.logger.debug("Read line #%i", self.read_lines)
        return json_obj # pass down the line as JSON Object

    def readLineRecord(self, line_number):
        """
        Read the given line from the file. The ``read_lines`` counter will be increased by one.
        The line location will be updated to the new line.

        **Returns**:
            The line corresponding the given line number, starting with 1.

        **Exceptions**:
            * If the line was already read an LinePassedError will be raised.
            * If the line does not excist a LineNotFoundError will be raised.
        """
        if self.current_line > line_number:
            raise LinePassedError("Line #%i has already been read" % line_number)

        current_read_lines = self.read_lines

        while((self.current_line < line_number) and (not self.isEOF())):
            line = self.readRecord()

        if self.isEOF():
            raise LineNotFoundError("Line #%i cannot be found in %s" % (line_number, self.file_name))

        self.read_lines = current_read_lines + 1 # reset to the accual read lines
        return line

    def isEOF(self):
        """
        Checks if the file is at its end.

		**Returns**:
			``True`` if there are no more files to handle.
        """
        return not bool(self.next_line)

    def close(self):
        """
        Cleanly closes the file at the end.
        """
        self.line_pointer.close()
        self.logger.info("Closed file %s after reading %i lines and standing an line #%i", self.file_name, self.read_lines, self.current_line)

class json_file_writer():
    """
    The writer class handles the writing to a file. It also handles the tmp files, to ensure that only complete data sets are passed on.

    **Parameters**:
        file_name : str
            The file location and name relative from the call location.
    """
    def __init__(self, file_name):
        self.file_name = file_name
        self.logger = logging.getLogger("CyberCaptain")
        self.logger.debug("Opening file %s", file_name)
        self.file_pointer = open("%s.tmp" % (file_name), "w")
        self.logger.debug("File %s is opened and ready to write to!", file_name)
        self.first = True

    def writeRecord(self, json_line):
        """
        Writes a json record to the file.

        **Parameters**:
            json_line : str

        """
        if not self.first: # manually add a new line before each line except the first one
            self.file_pointer.write("\n")
        self.file_pointer.write(json.dumps(json_line))
        self.file_pointer.flush() # ensure that every line is written instantly
        self.first = False

    def close(self):
        """
        Closes the file and removes the tmp suffix.
        """
        self.file_pointer.close()
        shutil.move("%s.tmp" % (self.file_name), self.file_name)

    def abort(self):
        """
        Closes the file without removing the tmp suffix.
        """
        self.file_pointer.close()
