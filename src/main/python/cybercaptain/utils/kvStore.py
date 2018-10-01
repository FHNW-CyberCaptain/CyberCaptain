"""
This util module handles the storage of keys and values. Built on top of the configobj library to not introduce more dependencies.
"""
import logging
import os
from configobj import ConfigObj

class kv_store():
    """
    The kvstore module allows to save keys with their string or list values to a specified store file and read from the specified file.

    **Parameters**:
		file_name   :   str
            The file location and name relative from call location.
    """
    def __init__(self, dir_name, file_name):
        self.logger = logging.getLogger("CyberCaptain")
        
        try:
            self.confi_obj = ConfigObj(os.path.join(dir_name, file_name), create_empty=True)
        except FileNotFoundError:
            self.logger.error("K/V store failed to initialize due to directories in path not existing.")

        self.logger.debug("K/V-Store initialized for file %s", file_name)

    def put(self, key, value, section=None, force=False):
        """
        Set the value of a key.

        **Parameters**:
            key     :   str
                The key of a value.
            value   :   str/list
                The string or list value of a key.

        **Optional**:
            section :   str
                specific section to where the key value should be written. allows grouping and useful for different modules separation.
            force   :   bool
                If force is set to ``True`` the newly added key will be directly written to the disk and not only kept in the memory.
                If this option is not used, don't forget to explicit call dump() after finishing to put all the keys.

		**Returns**:
			``True``.
        """
        if section:
            if section not in self.confi_obj.sections: self.confi_obj[section] = {}
            self.confi_obj[section][key] = value
        else:
            self.confi_obj[key] = value

        if force: self.dump()

        return True

    def get(self, key, section=None):
        """
        Gets the value of a key.

        **Parameters**:
            key     :   str
                The key of a value.

        **Optional**:
            section :   str
                specific section to from where get the value. If not set its expected to be in no group.

		**Returns**:
			``value`` if the key and its value has been found. ``None`` if no key was found.
        """
        if section: 
            if section in self.confi_obj.sections and key in self.confi_obj[section].keys(): 
                return self.confi_obj[section][key]
            return None
        if key in self.confi_obj.keys(): return self.confi_obj[key]
        return None

    def dump(self):
        """
        Saves the kvstore permanently to the disk.
        """
        self.confi_obj.write()

    def reload(self):
        """
        Reloads the config from the specific local file. Unpersisted settings will be lost.
        """
        self.confi_obj.reload()
