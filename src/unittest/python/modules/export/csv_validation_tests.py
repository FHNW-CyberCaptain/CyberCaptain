import unittest, os, shutil

from cybercaptain.export.csv import export_csv
from cybercaptain.utils.exceptions import ValidationError

# Append Needed Args - Related to Root Config projectName / projectRoot / moduleName
def append_needed_args(existing_args):
    return {**existing_args, 'projectRoot':os.path.join(os.path.dirname(__file__), '../assets/output'), 'projectName': "UNITTEST.cckv", 'moduleName': "UNITEST_MODULE"}

class ExportCSVValidationTest(unittest.TestCase):
    """
    Test the export csv validation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_validate_method(self):
        """
        Test if the validation works.
        """
        # Missing exportedAttributes Agument
        arguments = append_needed_args({
            "src":"",
            "target":""
        })

        with self.assertRaises(ValidationError):
            export_csv(**arguments)
