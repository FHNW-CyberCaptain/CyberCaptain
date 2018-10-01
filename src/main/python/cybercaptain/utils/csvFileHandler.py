"""
This util module handles all the CSV files for the CyberCaptain modules.
"""
import csv
import logging
import shutil

class csv_file_writer():
    """
    The writer class handles the writing to a file. It also handles the tmp files, to ensure that only complete data sets are passed on.

    **Parameters**:
        file_name : str
            The file location and name relative from the call location.
        header : list
            A list containing all the attributes which are concidered headres.
    """
    def __init__(self, file_name, header):
        self.file_name = file_name
        self.logger = logging.getLogger("CyberCaptain")
        self.file_pointer = open("%s.tmp" % (file_name), "w")
        self.csv_writer = csv.DictWriter(self.file_pointer, dialect='unix', fieldnames=header) # dialext unix is used cause it uses \n and quotes every entry
        self.csv_writer.writeheader()
        self.logger.debug("Opening file %s", file_name)

    def writeCSVRow(self, csv_row):
        """
        Writes a CSV formatted row. The passed ``dict`` must be flat. Any forgotten or non existend values will be left empty.

        **Parameters**:
            csv_row : dict
                The dict that has to be written down.
        """
        self.csv_writer.writerow(csv_row)

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
