""" 
This runCybercaptainGui module contains the Gooey GUI interpreter.
Make sure to have a python framework version and wxPython and Gooey installed!
""" 
import argparse
import sys
import os

from gooey import Gooey, GooeyParser
from runCybercaptain import main

IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'assets')

@Gooey(
	program_name='CyberCaptain - Arrr!',
	default_size=(800, 700),
	advanced=True,
	image_dir=IMAGE_DIR
)
def create_parser():
	"""
	This method creates the Gooey GUI parser which is used to parse inputs for CyberCaptain.

	**Returns**:
		``ArgumentParser`` with configured CC-Params.
	"""
	parser = GooeyParser(description="Verify, visualize and run your CyberCaptain script config file with ease.")
	parser._action_groups.pop()

	required = parser.add_argument_group('Main', gooey_options={'show_border': False,'columns': 2})
	optional = parser.add_argument_group('Specific Options', gooey_options={'show_border': False,'columns': 2 })

	required.add_argument("-c", "--config", help="CyberCaptain config file location", dest='config', required=True, widget="FileChooser")

	group_type = required.add_mutually_exclusive_group(required=True, gooey_options={'show_border': True})
	group_type.add_argument("-v", "--validate", help="validate config file and do not run", action="store_true")
	group_type.add_argument("-pv", "--pathvisualize", help="visualizes the path and do not run", action="store_true")
	group_type.add_argument("-run", "--run", help="run the configured script config file", action="store_true")

	optional.add_argument("-cp", "--customplaceholders", help="define and add a custom placeholder to the config", dest='customplaceholders')
	optional.add_argument("-mc", "--modulesconfig", help="overwrite cybercaptain modules config file location", widget="FileChooser")
	#optional.add_argument("-d", "--debug", help="set verbosity to debug and also redirect log output to stdout", action="store_true") # Default on with GUI for stdout output
	optional.add_argument("--overwritechecksum", help="overwrite the script config checksum if changed", action="store_true")
	optional.add_argument("--ignorechecksum", help="ignore the script config checksum check and continue on own risk", action="store_true")
	#optional.add_argument('others', nargs='*')  # Everything else - Added regarding pyb unittest arguments which will fail otherwise
	return parser

if __name__ == "__main__":
	args = create_parser().parse_args(sys.argv[1:])

	# Always debug to display stdout output to the GUI console
	args.debug = True 
	# Manual split customplaceholders incase more than one are defined, cant make usage of argparse on GUI input
	if args.customplaceholders:
		args.customplaceholders = dict(item.split("=") for item in args.customplaceholders.split(";"))
		
	main(args)