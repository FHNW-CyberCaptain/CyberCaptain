"""
The Clean module contains the processing_clean class.
"""
from cybercaptain.utils.helpers import str2bool
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.processing.base import processing_base
from cybercaptain.utils.jsonFileHandler import json_file_reader, json_file_writer

class processing_clean(processing_base):
    """
    The clean class allows to clean the data set of all unwanted attributes.

    **Parameters**:
        kwargs :
            contains a dictionary of all attributes.

    **Script Attributes**:
        format:
            <todo>
        keep:
            a list of JSON-attributes which will be kept, all others will be discarded. (cannot be used together with ``drop``)
        drop:
            a list of JSON-attributes which will be deleted, all others will be kept. (cannot be used together with ``keep``)
        ignoreMissingKeys:
            skip any missing keys if they are found. (cannot be used together with ``removeMissingKeys``)
        removeMissingKeys:
            remove any missing keys from the data set. (cannot be used together with ``ignoreMissingKeys``)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # TBD REFACTOR MOVE UP THE SINGLE STRING TO LIST

        # If subclass needs special variables define here
        self.format = kwargs.get("format")
        self.keep = kwargs.get("keep")
        self.drop = kwargs.get("drop")
        self.ignoreMissingKeys = str2bool(kwargs.get("ignoreMissingKeys"))
        self.removeMissingKeys = str2bool(kwargs.get("removeMissingKeys"))

    def run(self):
        """
        Runs the clean algorythm.
        """
        self.cc_log("INFO", "Data Processing Clean: Started")

        if self.format.lower() == "json":
            if self.drop and isinstance(self.drop, str): self.drop = [self.drop]
            if self.keep and isinstance(self.keep, str): self.keep = [self.keep]
            json_fr = json_file_reader(self.src)
            json_fw = json_file_writer(self.target)

            self.cc_log("INFO", "Started to clean line for line, please wait!")

            while not json_fr.isEOF():
                data = json_fr.readRecord()
                keepLine, cleaned_line = self.clean_json(data)
                self.cc_log("DEBUG", cleaned_line)
                if keepLine:
                    json_fw.writeRecord(cleaned_line)

            json_fr.close()
            json_fw.close()
        else:
            raise NotImplementedError("The defined format is not implement yet. Please add!")

        self.cc_log("INFO", "Data Processing Clean: Finished")
        return True

    def validate(self, kwargs):
        """
        Validates all arguments for the clean module.
        kwargs(dict): contains a dictionary of all attributes.
        """
        super().validate(kwargs)
        self.cc_log("INFO", "Data Processing Clean: started validation")
        if not kwargs.get("format"): raise ValidationError(self, ["format"], "Parameter cannot be empty!")
        if not kwargs.get("keep") and not kwargs.get("drop"): raise ValidationError(self, ["keep", "drop"] , "Parameters cannot be empty!")
        if kwargs.get("keep") and kwargs.get("drop"): raise ValidationError(self, ["keep", "drop"] , "Only one parameter can be defined!")

        if kwargs.get("drop") and not isinstance(kwargs.get("drop"), str) and not isinstance(kwargs.get("drop"), list): raise ValidationError(self, ["drop"], "Parameter has to be a string or list of strings!")
        if kwargs.get("keep") and not isinstance(kwargs.get("keep"), str) and not isinstance(kwargs.get("keep"), list): raise ValidationError(self, ["keep"], "Parameter has to be a string or list of strings!")

        if kwargs.get("ignoreMissingKeys") and kwargs.get("removeMissingKeys"): raise ValidationError(self, ["ignoreMissingKeys", "removeMissingKeys"] , "Parameters cannot be both defined!")
        if kwargs.get("ignoreMissingKeys") and not isinstance(kwargs.get("ignoreMissingKeys"), str): raise ValidationError(self, ["ignoreMissingKeys"], "Parameter has to be a string!")
        if kwargs.get("removeMissingKeys") and not isinstance(kwargs.get("removeMissingKeys"), str): raise ValidationError(self, ["removeMissingKeys"], "Parameter has to be a string!")
        self.cc_log("INFO", "Data Processing Clean: finished validation")

    def clean_json(self, data):
        """
        The passed line will be cleaned acording to the given attributes.
        data(dict): the line of one data entry.
        Returns the cleaned json line
        """
        if self.drop:
            return self.drop_in_json(data)
        else: # We should be sure its keep as prevalidation checks this - lowers coverage otherwise
            return self.keep_in_json(data)

    def drop_in_json(self, json_line):
        for attributes in self.drop:
            key_list = attributes.split('.')
            keepLine = self.deepdrop_json(json_line, key_list)	# If line has to be removed, return false otherwise no return
            if not keepLine: break
        return keepLine, json_line

    def keep_in_json(self, json_line):
        altered_line = {}
        for attributes in self.keep:
            key_list = attributes.split('.')
            keepLine = self.deepkeep_json(altered_line, json_line, key_list) # If line has to be removed, return false otherwise no return
            if not keepLine: break
        return keepLine, altered_line

    def deepdrop_json(self, the_dict, key_list):
        if the_dict and key_list[0] in the_dict:
            if len(key_list) == 1:
                del the_dict[key_list[0]]
                return True
            else:
                return self.deepdrop_json(the_dict[key_list[0]], key_list[1:])
        else:
            if self.ignoreMissingKeys:
                return True
            elif self.removeMissingKeys:
                return False
            else:
                raise KeyError("Key not existing")

    def deepkeep_json(self, altered_dict, the_dict, key_list):
        if the_dict and key_list[0] in the_dict:
            if len(key_list) == 1:
                altered_dict[key_list[0]] = the_dict[key_list[0]]
                return True
            else:
                if not key_list[0] in altered_dict: altered_dict[key_list[0]] = {}
                return self.deepkeep_json(altered_dict[key_list[0]], the_dict[key_list[0]], key_list[1:])
        else:
            if self.ignoreMissingKeys:
                return True
            elif self.removeMissingKeys:
                return False
            else:
                raise KeyError("Key %s not existing" % key_list)