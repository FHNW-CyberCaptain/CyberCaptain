"""
This module contains the processing diff class.
"""
from os import path, remove
from shutil import move
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.processing.base import processing_base
from cybercaptain.utils.jsonFileHandler import json_file_reader, json_file_writer
from cybercaptain.utils.kvStore import kv_store
from cybercaptain.utils.helpers import keyGen, genBTree

class processing_diff(processing_base):
    """
    The Diff module allows to analyse data over a time period it compares the new data with the latest saved.

    If there is no new data, it simply saves all the data given by the new set.

    If there is no change it will not change.

    If there is a change it will update the data set.

    **Parameters**:
        kwargs:
            contains a dictionary of all attributes.

    **Script Attributes**:
        keyAttributes:
            a list of id attriubutes with which a data record can be identified.
        attributesDiff:
            a list of attributes on which a diff must be made.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # If subclass needs special variables define here
        self.key_attributes = kwargs.get("keyAttributes")
        self.attributes_diff = kwargs.get("attributesDiff")
        # KV-Store Init
        self.kv_store = kv_store(self.projectRoot, self.projectName)
        self.time_id = path.basename(self.src)

    def target_exists(self):
        """
        Overwrites the base class method, cause the module merges the different runs into one file.

        **Returns**:
            ``False`` if this module has to be run, other wise ``True``.
        """
        if not path.isfile(self.target):
            return False
        else:
            last_src = self.kv_store.get("diff_last_src", section=self.moduleName)
            if not last_src:
                self.cc_log("INFO", "Data Processing Diff: The kv_store found no previous 'diff_last_src' - Need to run")
                return False
            current_src = self.time_id
            # check if the run ID is equals the last run
            return last_src == current_src

    def run(self):
        """
        Runs the diff algorythm.

        **Returns**:
            ``True`` if the run works fine.
        """
        self.cc_log("INFO", "Data Processing Diff: Started")
        if self.attributes_diff and isinstance(self.attributes_diff, str): self.attributes_diff = [self.attributes_diff]
        if self.key_attributes and isinstance(self.key_attributes, str): self.key_attributes = [self.key_attributes]

        # if the target does not exist create the file and add all the data
        if not path.isfile(self.target):
            json_fr = json_file_reader(self.src)
            self.cc_log("DEBUG", "Opened source file")
            json_fw = json_file_writer(self.target)
            self.cc_log("DEBUG", "Opened target file - please have patience")
            while not json_fr.isEOF():
                data = json_fr.readRecord()
                data = self.genDataSet(keyGen(self.key_attributes, data), data, self.attributes_diff)
                json_fw.writeRecord(data)
            json_fr.close()
            json_fw.close()
        # else create a B-Tree out of the src file with the nessecary data
        else:
            self.cc_log("DEBUG", "Generating B-Tree for the diff - please have patience")
            b_tree = genBTree(self.src, self.key_attributes)
            # move the old target so it can be read from and does not collide with the writer
            old_target = self.target + '.old'
            move(self.target, old_target)
            json_fr = json_file_reader(old_target)
            json_fw = json_file_writer(self.target)
            self.cc_log("INFO", "Started to generate the diff - please have patience")
            while not json_fr.isEOF():
                old_data = json_fr.readRecord()
                try: # update all the data
                    new_data = b_tree.pop(old_data["cc_id"])
                    diff_data = self.getDataByAttributes(self.attributes_diff, new_data)
                    old_data = self.compareData(old_data, diff_data)
                except KeyError: # if the id cannot be found it must be delete
                    old_data["cc_status"] = "delete"
                    old_data["cc_time_id"] = self.time_id
                json_fw.writeRecord(old_data)
            # add the left over data
            self.cc_log("INFO", "Adding leftover data...")
            while b_tree:
                key = b_tree.minKey()
                data = self.genDataSet(key, b_tree.pop(key), self.attributes_diff)
                json_fw.writeRecord(data)

            remove(old_target)
            json_fr.close()
            json_fw.close()

        self.kv_store.put(key="diff_last_src", value=(self.time_id), section=self.moduleName, force=True)
        self.cc_log("INFO", "Data Processing Diff: Finished")
        return True

    def validate(self, kwargs):
        """
        Validates all arguments for the diff module.

        **Parameters**:
            kwargs : dict
                contains a dictionary of all attributes.

        **Raises**:
            ValidationError: if the validation has failed
        """
        super().validate(kwargs)
        self.cc_log("INFO", "Data Processing Diff: started validation")
        if not kwargs.get("keyAttributes"):
            raise ValidationError(self, ["keyAttributes"], "Parameter cannot be empty!")
        if not kwargs.get("attributesDiff"):
            raise ValidationError(self, ["attributesDiff"], "Parameter cannot be empty!")
        self.cc_log("INFO", "Data Processing Diff: finished validation")

    def genDataSet(self, identifier, data, attributes, status="insert"):
        """
        Generates the data set for later use.

        **Parameters**:
            identifier : str
                The identifier of this data set.
            data : dict
                The entire data set passed down.
            attributes : list
                A list of attributes which define the key.
            status : str
                The status that has to be written into the data set. (Default is 'insert').

        **Returns**:
            A ``dict`` containing the wanted data as well as ``cc_status`` and ``cc_time_id``.
        """
        _data = {"cc_id": identifier, "cc_status": status, "cc_time_id": self.time_id}
        _data.update(self.getDataByAttributes(attributes, data))
        return _data

    def compareData(self, old_data, new_data):
        """
        Compares the given data sets and returns the updated set.

        **Parameters**:
            old_data : dict
                The old data which needs to be updated.
            new_data : dict
                The new data against which one has to be compared.

        **Returns**:
            The updated data set.
        """
        for key, value in new_data.items():
            if old_data[key] != value:
                old_data[key+"_PREVIOUS"] = old_data[key]
                old_data[key] = value
                old_data["cc_status"] = "update"
                old_data["cc_time_id"] = self.time_id
        if old_data["cc_status"] == "delete":
            old_data["cc_status"] = "insert"

        return old_data

    def getDataByAttributes(self, attributes, data):
        """
        Retreive all the attributes from the data.

        **Parameters**:
            attributes : list
                A list of attributes which define the key.
            data : dict
                The data for which the key has to be generated for.

        **Returns**: (dict)
            A ``dict`` with only the data with the given attributes.
        """
        result = {}

        for attribute in attributes:
            splitSet = attribute.split('.')
            _data = data
            for split in splitSet:
                _data = _data[split]
            result[attribute] = _data

        return result
