"""
This module contains the processing classing class.
"""
import re
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.utils.jsonFileHandler import json_file_reader, json_file_writer
from cybercaptain.utils.helpers import str2bool
from cybercaptain.processing.base import processing_base

class processing_classing(processing_base):
    """
    The classing allows to classify the data into the given rules.

	**Parameters**:
		kwargs:
			Contains a dictionary of all attributes.

    **Script Attributes**:
        classBy:
            The JSON-attribute on which must be classified.
        classes:
            A list of strings containing the class names.
        rules:
            A list of regular expressions containing the rules by which the data sets must be classified.
        keepOthers:
            A boolean whether the unmatchable data sets should be kept in an 'others' class or discarded.
        multiMatch:
            A boolean whether a single data set can be part of multiple classes, if set to false only the first match will be used.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # all subclass special script attributes
        self.class_by = kwargs.get('classBy')
        self.classes = kwargs.get('classes')
        self.rules = kwargs.get('rules')
        self.keep_others = str2bool(kwargs.get('keepOthers'))
        self.multi_match = str2bool(kwargs.get('multiMatch'))

    def run(self):
        """
        Runs the classing algorythm.
        """
        self.cc_log("INFO", "Data Processing Classing: Started")
        json_fr = json_file_reader(self.src)
        json_fw = json_file_writer(self.target)
        while not json_fr.isEOF():
            record = json_fr.readRecord()
            classes = self.getClasses(record)
            record['classes'] = classes
            json_fw.writeRecord(record)

        json_fr.close()
        json_fw.close()

        self.cc_log("INFO", "Data Processing Classing: Finished")
        return True

    def validate(self, kwargs):
        """
		Validates all arguments for the classing module.

		**Parameters**:
			kwargs : dict
				contains a dictionary of all attributes.
		"""
        super().validate(kwargs)
        self.cc_log("INFO", "Data Processing Classing: started validation")
        # check if empty
        if not kwargs.get('classBy'):
            raise ValidationError(self, ["classBy"], "Parameter cannot be empty!")
        if not kwargs.get('classes'):
            raise ValidationError(self, ["classes"], "Parameter cannot be empty!")
        if not kwargs.get('rules'):
            raise ValidationError(self, ["rules"], "Paramter cannot be empty!")
        if not kwargs.get('keepOthers'):
            raise ValidationError(self, ["keepOthers"], "Paramter cannot be empty!")
        if not kwargs.get('multiMatch'):
            raise ValidationError(self, ["multiMatch"], "Parameter cannot be empty!")

        # check if the attributes make sense
        if len(kwargs.get('classes')) != len(kwargs.get('rules')):
            raise ValidationError(self, ["classes", "rules"], "Parameters must be of same length!")
        self.cc_log("INFO", "Data Processing Classing: finished validation")

    def getClasses(self, record):
        """
        Determines the class or classes of the given JSON-Record.

        **Parameters**:
            record : obj
                The record to be classed.
        """
        attributes = self.class_by.split('.')
        classes = []

        for attribute in attributes:
            record = record[attribute]

        rule_no = 0
        for rule in self.rules:
            if re.search(rule, record) is not None:
                classes.append(self.classes[rule_no])
                rule_no += 1
                if self.multi_match is False:
                    break

        if self.keep_others is True and len(classes) <= 0:
            classes.append("others")

        return classes
