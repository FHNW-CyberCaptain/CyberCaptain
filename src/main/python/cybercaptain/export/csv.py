"""
This module contains the CSV export class.
"""

from cybercaptain.export.base import export_base
from cybercaptain.utils.exceptions import ValidationError, ConfigurationError
from cybercaptain.utils.jsonFileHandler import json_file_reader
from cybercaptain.utils.csvFileHandler import csv_file_writer

class export_csv(export_base):
    """
    The CSV exporting class exports the CyberCaptain data. This includes a morphing of JSON to CSV. This will flatten the JSON to one dimension, this cannot be undone. It is possible to keep the depth, but the exported data might be used to do further research or analysis where the additional columns or informations are confusing and useless.

    If a attribute is not found at a location, it will just be exported with the text ``CC-empty``. Cause if it is left empty, any further processing of the data might be flawed. It forces the user to think how to handle this data! (Just to be kind.)

	**Parameters**:
		kwargs:
			Contains a dictionary of all attributes.

    **Script Attributes**:
        exportedAttributes:
            * A list of attributes to be exported.
            * ``all``, all of the attributes will be exported. This will result in an extra loop over the entire data set.
            * ``line-number``, all the attributes of this line will be exported.
        attributeFill:
            The default value is ``CC-empty``, if you think you are smarter than what is documented then feel free to change this value.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # all subclass special script attributes
        self.exported_attributes = kwargs.get('exportedAttributes')

        # if int parse to int
        try: 
            self.exported_attributes = int(self.exported_attributes)
        except Exception:
            pass

        # if single string and not all parse to list
        if self.exported_attributes and isinstance(self.exported_attributes, str) and self.exported_attributes != "all": self.exported_attributes = [self.exported_attributes]

        if kwargs.get('attributeFill'):
            self.attribute_fill = kwargs.get('attributeFill')
        else:
            self.attribute_fill = 'CC-empty'
            self.cc_log("INFO", 'Set the filler attribute to "CC-empty"')

    def run(self):
        """
        Runs the csv export algorythm.
        """

        attributes = self.getAttributes(self.src)
        json_fr = json_file_reader(self.src)
        csv_fw = csv_file_writer(self.target, attributes)

        while not json_fr.isEOF():
            line = json_fr.readRecord()
            csv_row = {}
            # flatten the dict so that it can be written into the CSV format
            for key in attributes:
                val = self.getValueFromDict(line, key)
                if not val:
                    val = self.attribute_fill
                csv_row[key] = val
            csv_fw.writeCSVRow(csv_row)

        json_fr.close()
        csv_fw.close()

    def validate(self, kwargs):
        """
		Validates all arguments for the csv export module.

		**Parameters**:
			kwargs : dict
				contains a dictionary of all attributes.
        """
        super().validate(kwargs)
        if not kwargs.get('exportedAttributes'):
            raise ValidationError(self, ["exportedAttributes"], "Parameter cannot be empty!")

    def getAttributes(self, src):
        """
        Evaluates the given configuration and parses the attributes nessesary.

        **Parameters**:
			src : str
				The src location and name for opening the file.

        **Returns**:
            Returns a list of all wished attributes.
        """
        if isinstance(self.exported_attributes, list): # just return the given list of attributes
            return self.exported_attributes

        json_fr = json_file_reader(src)
        if isinstance(self.exported_attributes, int): # find the line and it's attributes
            line = json_fr.readLineRecord(self.exported_attributes)
            attributes = self.getKeysFromDict(line)
            json_fr.close()
            return attributes
        if self.exported_attributes == 'all': # find all the attributes of the given file
            attributes = self.getAllKeysFromFile(json_fr)
            json_fr.close()
            return attributes
        else:
            raise ConfigurationError("Unknown attributes to export")

    def getKeysFromDict(self, s_dict, prefix=""):
        """
        Finds all keys within the dict. Including nested dicts.

        **Parameters**:
			s_dict : dict
				Contains the dict of which all attributes must be retrived from.

        **Returns**:
            Returns a list of all keys from the given dict.
        """
        keys = []
        for k in s_dict.keys():
            key_with_prefix = ""
            if not prefix:
                key_with_prefix = k
            else:
                key_with_prefix = "%s.%s" % (prefix, k)

            keys.append(key_with_prefix)

            if isinstance(s_dict[k], dict):
                # get all keys in a set
                n_keys = set(self.getKeysFromDict(s_dict[k], key_with_prefix))
                s_keys = set(keys)
                diff = n_keys - s_keys # get only the new keys a.k.a. the difference
                keys = keys + list(diff) # add the new attributes

        return keys

    def getAllKeysFromFile(self, json_fr):
        """
        Find all keys in the given file handler.

        **Parameters**:
			json_fr : json_file_reader
				The file reader with the open file.

        **Returns**:
            Returns a list of all keys from the given file.
        """
        keys = []
        while not json_fr.isEOF():
            line = json_fr.readRecord()
            n_keys = set(self.getKeysFromDict(line))
            s_keys = set(keys)
            diff = n_keys - s_keys
            keys = keys + list(diff)

        return keys

    def getValueFromDict(self, dictionary, attribute):
        """
        Returns the value of the given attribute from the given dictionary. The Attributes are split by '.'.

        **Parameter**:
            dictionary : dict
                The dictionary which has to be searched.
            attribute : str
                The attribute for which has to be searched for.

        **Returns**:
            Returns the value of the attribute.
        """
        
        if "." in attribute:
            for key in attribute.split("."):
                dictionary = dictionary[key]
            return dictionary
        else:
            return dictionary[attribute]
        
