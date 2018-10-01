"""
This module contains the processing base class.
"""
from cybercaptain.base import cybercaptain_base

class processing_base(cybercaptain_base):
	"""
	This is the base class for the processing classes.

	**Parameters**:
		kwargs :
			contains a dictionary of all attributes.
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	# Run Method To Run Wanted Task - Needs To Be Implemented By Subclass
	def run(self):
		"""
		The run method is not implemented here and must be over written by the child class.

		**Raises**:
			NotImplementedError
		"""
		raise NotImplementedError("data_processing: Subclass must implement the run method")

	def validate(self, kwargs):
		"""
		The validate mehtod checks all to processing common attributes and passes this on to the parent class to check CyberCaptain common attributes.
		"""
		super().validate(kwargs)

	def depends_on_file(self):
		"""
		Needs to be implemented by specific processing modules for functionality.
		Can be used to wait for a different path to finish before running this task due to a different file needs to be created first.
		
		**Returns**:
			``False`` as a default.
			``str`` with the depending attribute name where the depending file is defined.
		"""
		return False

