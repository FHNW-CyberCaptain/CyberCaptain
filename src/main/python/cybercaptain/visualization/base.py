"""
This module contains the visualization base class.
"""
from cybercaptain.base import cybercaptain_base

class visualization_base(cybercaptain_base):
    """
    This is the base class for the visualization classes.

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
        raise NotImplementedError("data_visualization: Subclass must implement the run method")

    def validate(self, kwargs):
        """
        The validate mehtod checks all to processing common attributes and passes this on to the parent class to check CyberCaptain common attributes.

		**Parameters**:
			kwargs : dict
				contains a dictionary of all attributes.
        """
        super().validate(kwargs)
