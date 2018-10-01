"""
This module contains the processing group class.
"""
import re
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.processing.base import processing_base
from cybercaptain.utils.jsonFileHandler import json_file_reader, json_file_writer

class processing_group(processing_base):
    """
    The grouping allows to aggregate same attributes into one data set.

    **Parameters**:
        kwargs:
            contains a dictionary of all attributes.

    **Script Attributes**:
        groupby:
            The JSON-attribute on which must be grouped.
        groupRegex:
            (Optional) If the attribute is a String and the grouping is done within a subgroup of it.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # If subclass needs special variables define here
        self.groupBy = kwargs.get("groupby")
        self.groupRegex = kwargs.get("groupRegex")

    def run(self):
        """
        Runs the group algorythm.
        """
        self.cc_log("INFO", "Data Processing Group: Started")
        data_dict = {}
        json_fr = json_file_reader(self.src)
        json_fw = json_file_writer(self.target)
        # load data
        self.cc_log("DEBUG", "Started to group, please wait...!")
        while not json_fr.isEOF():
            data = json_fr.readRecord()
            for attribute in self.groupBy.split('.'):
                data = data.get(attribute, {})

            if not data: 
                self.cc_log("DEBUG", "Skip a line, attribute was not found!")
                continue # Skip as attribute seems to not be found 

            # check if the groupRegex is set and get the first group of it
            if self.groupRegex:
                data = re.search(self.groupRegex, data)
                if not data or not data.group(0):
                    data = "others"
                else:
                    data = data.group(0)
                self.cc_log("DEBUG", "Regex grouped %s" % data)

            if data in data_dict:
                data_dict[data] += 1
            else:
                data_dict[data] = 1

        for entry in self.dictToList(data_dict):
            json_fw.writeRecord(entry)

        json_fr.close()
        json_fw.close()
        self.cc_log("INFO", "Data Processing Group: Aggregated the data set into " + str(len(data_dict.keys())) + " data entries")
        self.cc_log("INFO", "Data Processing Group: Finished")
        return True

    def validate(self, kwargs):
        """
        Validates all arguments for the group module.

        **Parameters**:
            kwargs : dict
                contains a dictionary of all attributes.
        """
        super().validate(kwargs)
        self.cc_log("INFO", "Data Processing Group: started validation")
        if not kwargs.get("groupby"): raise ValidationError(self, ["groupby"], "Parameter cannot be empty!")
        self.cc_log("INFO", "Data Processing Group: finished validation")

    def dictToList(self, dictionary):
        """
        Converts a dict into a list.

        **Parameters**:
            dictionary : dict
                The dict to be converted.
        """
        _list = []
        for key, value in dictionary.items():
            _list.append({"group":key, "count":value})

        return _list
