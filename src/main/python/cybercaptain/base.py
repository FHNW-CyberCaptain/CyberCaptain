"""
This module contains the overa all base class.
"""
import logging
import os
from pathlib import Path
from cybercaptain.utils.exceptions import ValidationError

class cybercaptain_base(object):
	"""
	This is the base class for all CyberCaptain modules.

	**Parameters**:
		kwargs:
			contains a dictionary of all attributes.

	**Script Attributes**:
		projectName:
			defines the defined name of the current running script config.
		projectRoot:
			defines the defined folder where the project should be run in.
		moduleName:
			defines the unique identifier name of the current module.
		src:
			defines where the source can be found.
		target:
			defines where the file must be written to. This must be unique over the whole script.
	"""
	def __init__(self, **kwargs):
		self.projectName = kwargs.get("projectName")
		self.projectRoot = kwargs.get("projectRoot")
		self.moduleName = kwargs.get("moduleName")
		self.logger = logging.getLogger("CyberCaptain")

		self.src = kwargs.get("src")
		self.target = kwargs.get("target")

	def target_exists(self):
		"""
		Check if the given target is a file.
		"""
		return Path(self.target).is_file()

	def run(self):
		"""
		The run method is not implemented here and must be over written by the child class.
		
		**Raises**:
			NotImplementedError
		"""
		raise NotImplementedError("CyberCaptainBase: Subclasses must implement the run method")

	def validate(self, kwargs):
		"""
		The validate mehtod checks all to processing common attributes and passes this on to the parent class to check CyberCaptain common attributes.

		**Parameters**:
			kwargs : dict
				contains a dictionary of all attributes.
		"""
		self.cc_log("INFO", "CyberCaptain Base: started validation")
		if not kwargs.get("src"):
			raise ValidationError(self, ["src"], "Parameter cannot be empty!")
		if not kwargs.get("target"):
			raise ValidationError(self, ["target"], "Parameter cannot be empty!")

		self.cc_log("INFO", "CyberCaptain Base: finished validation")

	def pre_check(self):
		"""
		Needs to be implemented by specific modules for functionality.
		Run a pre-check to check for stuff before the run.
		
		**Returns**:
			``True`` if success, ``False`` if failed. Skip the path if failed.
		"""
		return True
		
	def post_check(self):
		"""
		Needs to be implemented by specific modules for functionality.
		Run a post-check to check for stuff after the run.
		
		**Returns**:
			``True`` if success, ``False`` if failed. Skip the following path if failed.
		"""
		return True

	def cc_log(self, lvl, message):
		"""
		Unifies the log message for the modules.
		Adds more infos to pinpoint the log origin.
		"""
		log_lvl = getattr(self.logger, lvl, -99)
		if log_lvl == -99: log_lvl = 20 # If for given lvl no logger lvl is found set to 20 == INFO
		self.logger.log(log_lvl, "[%s] - %s" % (self.moduleName, message))