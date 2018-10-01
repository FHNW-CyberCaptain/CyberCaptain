"""
This module contains the store local class.
"""
import json
from pathlib import Path
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.store.base import store_base
from cybercaptain.utils.jsonFileHandler import json_file_reader, json_file_writer

class store_local(store_base):
	"""
	The local module allows to integrate CyberCaptain data from a connected file system.

	**Important**:
		This module currently only serves as a place to implement local imports with for example the need to morph the data.
		If the local to import file already is a json datasets newline separated file, we recommend to directly include 
		it in the src attribute of the next configured module.
	
	**Parameters**:
		kwargs:
			contains a dictionary of all attributes.

	**Script Attributes**:
		format:
			<todo>
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.validate(kwargs)
		# If subclass needs special variables define here
		self.format = kwargs.get("format")

	def run(self):
		"""
		Runs the local algorythm.
		"""
		self.cc_log("INFO", "Data Store Local: Started")
		self.cc_log("INFO", "Run DataStore LOCAL for (src->target) %s -> %s" % (self.src, self.target))

		# TBD: Rework this in Task #10
		count = 0
		if self.format.lower() == "json":
			json_fr = json_file_reader(self.src)
			json_fw = json_file_writer(self.target)

			self.cc_log("INFO", "Started to read the local file into a new file, please wait!")

			while not json_fr.isEOF():
				data = json_fr.readRecord()
				json_fw.writeRecord(data)

			json_fr.close()
			json_fw.close()
		else:
			raise NotImplementedError("The selected format is not implemented!")
		# END TEMP
		self.cc_log("DEBUG", "Data Store Local: Loaded %s data entries" % (count))
		self.cc_log("INFO", "Data Store Local: Finished")

		return True

	def validate(self, kwargs):
		"""
		Validates all arguments for the local module.

		**Parameters**:
			kwargs : dict
				contains a dictionary of all attributes.
		"""
		super().validate(kwargs)
		self.cc_log("INFO", "Data Store Local: started validation")

		# Check if src file to load exists
		if not Path(kwargs.get("src")).is_file() and not Path(self.src).is_file():
			raise ValidationError(self, ["src"], "Parameter must point to an existing file!")

		self.cc_log("INFO", "Data Store Local: finished validation")
