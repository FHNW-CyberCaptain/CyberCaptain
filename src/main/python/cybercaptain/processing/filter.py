"""
This module contains the processing filter class.
"""
import re
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.processing.base import processing_base
from cybercaptain.utils.jsonFileHandler import json_file_reader, json_file_writer

class processing_filter(processing_base):
    """
    The filter allows to filter the data sets based on the given filter attribute.

    **Parameters**:
        kwargs:
            contains a dictionary of all attributes.

    **Script Attributes**:
        filterby:
            the JSON-attribute on which must be filtered
        rule:
            defines the rule by which must be filtered. It consits of two fields: the rule type and the rule itself
            rule types can be:
                * ``RE``: Regular Expression, the only way to filter strings!
                * ``GE``: Greater Equals
                * ``GT``: Greater Than
                * ``EQ``: Equals
                * ``LT``: Less Than
                * ``LE``: Less Equals
                * ``NE``: Not Equals, does not work with strings!
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # If subclass needs special variables define here
        self.filterby = kwargs.get("filterby")
        self.rule = kwargs.get("rule")

    def run(self):
        """
        Runs the filter algorythm.
        """
        self.cc_log("INFO", "Data Processing Filter: Started")
        count = 0
        json_fr = json_file_reader(self.src)
        json_fw = json_file_writer(self.target)
        # load data
        self.cc_log("DEBUG", "Started to filter, please wait...!")
        while not json_fr.isEOF():
            data = json_fr.readRecord()
            if self.filter(data):
                json_fw.writeRecord(data)
            else:
                count += 1

        json_fr.close()
        json_fw.close()
        self.cc_log("INFO", "Data Processing Filter: Filtered " + str(count) + " data sets")
        self.cc_log("INFO", "Data Processing Filter: Finished")
        return True

    def validate(self, kwargs):
        """
        Validates all arguments for the filter module.

        **Parameters**:
            kwargs : dict
                contains a dictionary of all attributes.
        """
        super().validate(kwargs)
        self.cc_log("INFO", "Data Processing Filter: started validation")
        if not kwargs.get("filterby"):
            raise ValidationError(self, ["filterby"], "Parameter cannot be empty!")
        if not kwargs.get("rule"):
            raise ValidationError(self, ["rule"], "Parameter cannot be empty!")

        match = re.search("(^\w\w)\s(.*)", kwargs.get("rule"))
        if not match:
            raise ValidationError(self, ["rule"], "Parameter must start with an operator!")
        if not match.group(2):
            raise ValidationError(self, ["rule"], "Parameter must end with a value!")

        self.cc_log("INFO", "Data Processing Filter: finished validation")

    def filter(self, data):
        """
        This method decides if a given line must be filtered or not.

        **Parameters**:
            line : str
                contains one data entry of the source file in JSON fomrat.

        **Returns**:
            ``True`` if the line should be kept, and ``False`` if the line can be discarded.
        """
        attributes = self.filterby.split('.')

        for attribute in attributes:
            data = data.get(attribute, {})

        if not data: 
            self.cc_log("DEBUG", "Skipped line for not existing attribute")
            return False # Skip as attribute seems to not be found 

        match = re.search("(^\w\w)\s(.*)", self.rule)
        # TBD what if int is in a string in the json
        if match.group(1) == "RE":
            if re.search(match.group(2), data) is not None:
                return True

        if match.group(1) == "GT":
            if int(data) > int(match.group(2)):
                return True

        if match.group(1) == "GE":
            if int(data) >= int(match.group(2)):
                return True

        if match.group(1) == "EQ":
            if int(data) == int(match.group(2)):
                return True

        if match.group(1) == "LT":
            if int(data) < int(match.group(2)):
                return True

        if match.group(1) == "LE":
            if int(data) <= int(match.group(2)):
                return True

        if match.group(1) == "NE":
            if int(data) != int(match.group(2)):
                return True
        self.cc_log("DEBUG", "Data Processing Filter: filtereded out line: %s" % data)
        return False
