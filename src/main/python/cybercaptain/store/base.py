"""
This module contains the store base class.
"""
from cybercaptain.base import cybercaptain_base

class store_base(cybercaptain_base):
	"""
	This is the base class for the store classes.

	**Parameters**:
		kwargs:
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
		raise NotImplementedError("data_store: Subclass must implement the run method")

	def validate(self, kwargs):
		"""
		The validate mehtod checks all to processing common attributes and passes this on to the parent class to check CyberCaptain common attributes.
		"""
		super().validate(kwargs)

	def inject_additional_tasks(self):
		"""
		Needs to be implemented by specific store modules for functionality.
		Can be used to inject additional tasks for example if a store module needs to load missing datasets.
		
		**Returns**:
			``False`` as a default, [] list of dicts with {"attributes":{KWARGS}, "identifier":"zz"}
		"""
		return False
