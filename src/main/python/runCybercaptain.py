""" 
This runCybercaptain module contains the CyberCaptain class.
""" 
import argparse
import fnmatch
import importlib
import os
import re
import sys
import time
import logging
import glob

from configobj import ConfigObj, ConfigObjError

from cybercaptain import *
from cybercaptain.utils.helpers import fileExists, is_valid_url, make_sha1, str2bool, get_file_extension, append_str_to_filename
from cybercaptain.utils.logging import setup_logger, shutdown_logger
from cybercaptain.utils.exceptions import ValidationError, ConfigurationError
from cybercaptain.utils.kvStore import kv_store
from cybercaptain.utils.pathVisualizer import run_path_visualisation

DEFAULT_MODULES_CONFIG_FILE = "modules.ccc" # Default modules config file name
DEFAULT_MODULES_CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) + "/" +DEFAULT_MODULES_CONFIG_FILE # Default modules config location

class CyberCaptain:
	"""The CyberCaptain class allows to run and validate a preconfigured task script file. 

	The preconfigured task script will be tested and run if executed. If the module wants to be used directly please fill in all the parameters. 
	Via CLI it is possible to execute as follows:
		$ python runCybercaptain.py -c path/to/scriptFile.ccs
	If there are custom placeholders {xy} defined in the script file the usage is as follows:
		$ python runCybercaptain.py -c path/to/scriptFile.ccs -cp xy=1
	If there is the need for a custom module config file and for example only register custom modules, the usage is as follows:
		$ python runCybercaptain.py -c path/to/scriptFile.ccs -mc path/to/custom/moduleConf.ccc
	If only a validation of the script file is needed without any run:
		$ python runCybercaptain.py -c path/to/scriptFile.ccs -v
	If the log output should be redirected to stdout:
		$ python runCybercaptain.py -c path/to/scriptFile.ccs -v -d


	**Parameters**: 
	config: path
		a path to the script config containing all tasks
	modulesConfig: path
		a path to the modules config file containing all modules, defaults to DEFAULT_MODULES_CONFIG_PATH
	validate: boolean
		a boolean if the config should only be validated but not be run
	customplaceholders: dict
		a dict containing all set custom placeholders to be replaced in the script config file
	debug: boolean
		a boolean if the log output should be redirected to stdout
	overwritechecksum: boolean
		a boolean to overwrite the calculated checksum of the script config check
		Example usage: If in the script configuration for example only a processing module is changed, we don't want to lose all the keys/values
			written to the KV-Store by deleting the KV-Store. Call the run once with '--overwritechecksum' to update the checksum.
		Recommended usage: If things in the script configuration were changed, we recommend to "reset" the project by deleting all files in the projectRoot
			(including the KV-Store) to minimize problems and issues.
	ignorechecksum: boolean
		a boolean to force suppress the checksum script config check (NOT RECOMMENDED)
		Example usage: While developing and creating the script configuration file the checksum will change alot. Call the run with '--ignorechecksum'
			to suppress the checksum check warning. If the development is finished make usage of the '--overwritechecksum' to update to the most recent.
		Recommended usage: If things in the script configuration were changed, we recommend to "reset" the project by deleting all files in the projectRoot
			(including the KV-Store) to minimize problems and issues.
	pathVisualize: boolean
		a boolean if only the path should be visualized. outputs a html file with the path visualized. 
	"""
	def __init__(self, config, modulesConfig, validate, customplaceholders, debug, overwritechecksum=False, ignoreChecksum=False, pathVisualize=False):
		self.config = config
		self.modulesConfig = modulesConfig
		self.validate = validate
		self.cphs = customplaceholders
		self.overwritechecksum = overwritechecksum
		self.ignoreChecksum = ignoreChecksum
		self.pathVisualize = pathVisualize

		self.loaded_conf = None
		self.loaded_modules_conf = None

		self.logger = setup_logger(debug=debug, log_location=self.get_log_location()) # Setup the logger for CyberCaptain

		self.logger.info("[CC-RUN] - >> Started CyberCaptain with params (-c %s, -mc %s, -v %s, -cp %s, -d %s, --overwritechecksum %s, --ignorechecksum %s, --pathvisualize %s)" 
		% (config, modulesConfig, validate, customplaceholders, debug, overwritechecksum, ignoreChecksum, pathVisualize))

		if not fileExists(self.config):
			self.logger.error("[CC-RUN] - FileNotFoundError: Please define an existing CyberCaptain-Script-Config file!")
			raise FileNotFoundError("Please define an existing CyberCaptain-Script-Config file!")

		if not fileExists(self.modulesConfig):
			self.logger.error("[CC-RUN] - FileNotFoundError: Please define an existing CyberCaptain-Modules-Config file!")
			raise FileNotFoundError("Please define an existing CyberCaptain-Modules-Config file!")

		try:
			self.loaded_conf = ConfigObj(self.config)
			self.loaded_conf.walk(self.replace_placeholders_walker) # Issue 25, Walk trough config to replace placeholders
			self.loaded_conf.walk(self.append_project_root_path_walker) # Issue 25, Walk trough config to replace placeholders	
		except ConfigObjError as coe:
			self.logger.error("[CC-RUN] - Failed to parse script config file (Line #%s '%s') - Remember to have unique section names!" % (coe.line_number, coe.line))
			raise

		try:
			self.loaded_modules_conf = ConfigObj(self.modulesConfig)
		except ConfigObjError as coe:
			self.logger.error("[CC-RUN] - Failed to parse modules config file (Line #%s '%s') - Please recheck!" % (coe.line_number, coe.line))
			raise
		
		if self.validate or self.pathVisualize:
			self.logger.info("[CC-RUN] - Validate the config file")
			self.logger.debug(self.loaded_conf)
			self.validate_config(self.loaded_conf, self.loaded_modules_conf)

			if self.pathVisualize:
				self.logger.info("[CC-RUN] - Visualize the config path")
				task_paths = self.get_all_task_paths(self.loaded_conf, self.loaded_modules_conf)
				run_path_visualisation(task_paths, self.loaded_conf, self.loaded_modules_conf)
		else:
			self.logger.info("[CC-RUN] - Running the config file")
			self.logger.debug(self.loaded_conf)
			self.validate_config(self.loaded_conf, self.loaded_modules_conf) 
			self.run_config(self.loaded_conf, self.loaded_modules_conf)

	def __del__(self):
		"""
		Called on CyberCaptain end.
		"""
		shutdown_logger()

	def validate_config(self, config, modules_config):
		"""
		This method validates a given script config file and the modules config.

		**Parameters**: 
		config: path
			a path to the script config containing all tasks
		modulesConfig: path
			a path to the modules config file containing all modules, defaults to DEFAULT_MODULES_CONFIG_PATH
		"""
		self.logger.info("Verify the Config...")

		# Validate if a projectName is given
		if "projectName" not in config:
			self.logger.error("[CC-RUN] - The CyberCaptain config file needs to have a projectName (projectName=XY)")
			raise KeyError("The CyberCaptain config file needs to have a projectName (projectName=XY)")

		# Validate if the project root dir is set
		if "projectRoot" not in config:
			self.logger.error("[CC-RUN] - The CyberCaptain config file needs to have the project root defined (projectRoot=/xyz/abc)")
			raise KeyError("The CyberCaptain config file needs to have the project root defined (projectRoot=/xyz/abc)")

		# Validate ProjectRoot to be an absolute path
		if not os.path.isabs(config['projectRoot']):
			raise ConfigurationError("Please define an absolute path as projectRoot!")

		# Validate ProjectRoot to be an existing path
		if not os.path.isdir(config['projectRoot']):
			raise ConfigurationError("The projectRoot path seems to not be existing - please create!")

		# Validate modules config
		if "restricted_target_modules" not in modules_config: modules_config["restricted_target_modules"] = []
		if "wildcard_src_modules" not in modules_config: modules_config["wildcard_src_modules"] = []
		
		# Validate sources and targets
		all_sources = [config[s]["src"] for s in config.sections if "src" in config[s]]
		all_targets = [config[s]["target"] for s in config.sections]

		# Validate if all sources and targets have a file extension - introduced by #72 to be able to inject placeholder ourselves
		if not self.paths_have_file_extensions(all_sources): raise ConfigurationError("Please define a file extension for all sources!")
		if not self.paths_have_file_extensions(all_targets): raise ConfigurationError("Please define a file extension for all targets!")

		if len(all_targets) != len(set(all_targets)):
			raise ConfigurationError("Script config contains duplicated TARGETs, please use a different TARGET for every task!")		

		for s in config.sections: # Loop through all sections and verify
			ss = s.split(" ")
			if(len(ss) != 2): # Tasks need module name plus unique name
				raise ConfigurationError("Config for %s is missing the module and/or name ([moduleName uniqueIdentifier])!" % (s))

			# Issue 67 - Name and ProjectRoot are reserved root config attributes so can not exist in any module conf
			if "projectName" in config[s] or "projectRoot" in config[s] or "moduleName" in config[s]:
				raise ConfigurationError("Module configuration for %s can not contain an attribute called 'projectName', 'projectRoot' or 'moduleName'!" % (s))

			s_module, s_name, *identifier = s.split(" ")
			
			if s_module.lower() not in modules_config.keys(): # Check if the configured module also exists in the modules config
				raise ConfigurationError("The configured module (%s) is not present in the modules config (Unknown). Please add!" % (s_module.lower()))

			if s_module.lower() in modules_config["restricted_target_modules"] and config[s]["target"] in all_sources: # Special rules for the restricted modules
				raise ConfigurationError("The configured module (%s) is a restricted module but its TARGET is used as a SRC in another module!" % (s_module.lower()))
		
			if (s_module.lower() not in modules_config["no_src_modules"]) and (not fileExists(config[s]["src"])): # File does not exist already
				if config[s]["src"] not in all_targets and not is_valid_url(config[s]["src"]): # File will never be generated but also check if its a URL as there isnt ever a file if URL
					if s_module.lower() in modules_config["wildcard_src_modules"]: # Special rules for the wildcard SRC modules
						if len(fnmatch.filter(all_targets, config[s]["src"])) <= 0 and len(glob.glob(config[s]["src"])) <= 0: # Check all targets for a matching file with the wildcard source
							raise ConfigurationError("Wildcard matching source file (%s) will never be generated (or file does not exist as a TARGET or module not defined as a wildcard_src_modules in the modules config), please recheck!" % (config[s]["src"]))
					else:
						raise ConfigurationError("Source file (%s) will never be generated (or file does not exist as a TARGET or module not defined as a wildcard_src_modules in the modules config or if its a first module the src might be not existing), please recheck!" % (config[s]["src"]))
			else:
				if s_module.lower() not in modules_config["no_src_modules"]:
					if config[s]["src"] in all_targets: # File does exist physical and is in targets so will be overwritten
						self.logger.warning("[CC-RUN] - File (%s) does already exist! Please recheck to not overwrite anything" % (config[s]["src"]))
				else:
					# No src module as some modules do not require a SRC - for example censys if data gets fetched via API, if there are conditions that SRC is still needed it has to be checked manually in the validation method
					# E.g. censys data can also be fetched via direct url, for that SRC is needed -> This is checked in the validation if viaApi is false it has to contain a src
					self.logger.debug("[CC-RUN] - Detected a no src module - please make sure you do not need a SRC for the current configuration.")
					
			# Issue 67 - Pass root config variables to the modules
			root_confs = {key: config[key] for key in config if not isinstance(config[key], dict)}

			mod = self.get_class_by_module_conf_key(modules_config[s_module])(**{**config[s], **root_confs, **{'moduleName': s_name}}) # Get the module out via modules_config and fill in the parameters which will be verified in each class & Issue 67 root conf & moduleName attributes
			
			# Issue 94 - Verify that the a depending file module file also gets created or is existing
			if "depends_on_file" in dir(mod):
				dep_attribute = mod.depends_on_file()
				if dep_attribute and not fileExists(config[s][dep_attribute]) and config[s][dep_attribute] not in all_targets:
					raise ConfigurationError("A depending file (%s) for the module (%s) is not existing and will not be created by any other task!" % (config[s][dep_attribute], s_module.lower()))

		self.logger.info("[CC-RUN] - >> Verified!")

	def run_config(self, config, modules_conf):
		"""
		This method runs a given script config file and the modules config.

		**Parameters**: 
		config: path
			a path to the script config containing all tasks
		modulesConfig: path
			a path to the modules config file containing all modules, defaults to DEFAULT_MODULES_CONFIG_PATH
		"""
		# Check the checksum of the script config - if it has changed from the previous run stop the run.
		# Only check on run as the validate method is used to check for wrong configs.
		# Can be bypassed with the --ignorechecksum flag (not recommended)
		if not self.checksum_check(config['projectName'], config['projectRoot'], self.config):
			raise ConfigurationError("The script config has changed from previous run - please make use of the checksum flags or delete the KV-Store if a complete new run should be done!") 
		
		self.logger.info("[CC-RUN] - Running the Config...")

		# Issue 67 - Pass root config variables to the modules
		root_confs = {key: config[key] for key in config if not isinstance(config[key], dict)}

		# Get all the task paths
		task_paths = self.get_all_task_paths(config, modules_conf)

		# Check the all task paths which task has to run and which doesnt
		self.logger.info("[CC-RUN] - Detected %s path(s)!" % (len(task_paths)))

		task_paths_counter = 0
		while task_paths_counter < len(task_paths):
			self.logger.info("[CC-RUN] - Running Path: %s" % " -> ".join(list(reversed(task_paths[task_paths_counter]))))
			for n in list(reversed(task_paths[task_paths_counter])): # Reverse the task list and start from top to bottom
				s_module, s_name, *identifier = n.split(" ")

				module = self.get_class_by_module_conf_key(modules_conf[s_module])(**{**config[n], **root_confs, **{'moduleName': s_name}}) # Module for respective task & Issue 67 - root confs & moduleName appended

				if not module.target_exists():
					self.logger.info("[CC-RUN] - Task %-40s - %-40s - %-4s" % (n, "Target file has not been created before", "Try to run!"))

					try:
						# Issue 94 - Processing modules can depend on files which are generated from another path in the script config (e.g. join)
						depends_on_file_and_not_exists = self.check_depends_on_file_and_not_exists(config, n, module)
						if depends_on_file_and_not_exists:
							if task_paths_counter+1 < len(task_paths): # Check if the depends on file path is the last path or not, indicates if the needed file still can be generated
								self.logger.info("[CC-RUN] - Depending file (%s) for module %s with name %s is not ready yet, we try again later!" % (depends_on_file_and_not_exists, s_module, s_name))
								task_paths.append(task_paths[task_paths_counter])
								self.logger.info("[CC-RUN] - This current path will be skipped and continued after the other paths have finished!")
								break
							else: # Prevents forever waiting for the file - if its the last path it will not be generated anymore if still missing (e.g. API new data expected but no new available)
								self.logger.warning("[CC-RUN] - Depending file (%s) for module %s with name %s was never generated and no other paths are left - skip!" % (depends_on_file_and_not_exists, s_module, s_name))
								break

						# Issue 72 - Look for additional tasks to inject (Missing Datasets)
						# Needs to be executed before any pre/post_check and run of the main task as if main did run already rest will be skipped too
						additional_paths = self.check_and_get_additional_paths(task_paths, task_paths_counter, config, n, module)
						if additional_paths:
							self.logger.info("[CC-RUN] - Extending the current run with %d additional path(s)" % len(additional_paths))
							task_paths.extend(additional_paths)
							# Append the current task we are on to the newly injected paths ending as we need to process the injected first
							task_paths.append(task_paths[task_paths_counter])
							self.logger.info("[CC-RUN] - This current path will be skipped and run after the additional paths!")
							break # Skip this path - As it will be run at the end again
							
						if not module.pre_check(): # Issue 71 - Precheck
							self.logger.error("[CC-RUN] - Task %s did not pass the pre check - rest of the path will be skipped. Please recheck!" % n)
							break # Module pre check did not return true, skip path and log incident
						if not module.run(): # Run the module
							self.logger.warning("[CC-RUN] - Task %s did not run successfully or was skipped - rest of the path will be skipped. Please recheck!" % n)
							break # Module run did not return true, skip path and log incident
						if not module.post_check(): # Issue 71 - Postcheck
							self.logger.error("[CC-RUN] - Task %s did not pass the post check - rest of the path will be skipped. Please recheck!" % n)
							break # Module post check did not return true, skip path and log incident
					except Exception as e:
						self.logger.exception(e)
						self.logger.error("[CC-RUN] - Fatal error in task %s - skip the path!" % n)
						break
				else:
					self.logger.info("[CC-RUN] - Task %-40s - %-40s - %-4s" % (n,"Target file is existing", "Skip the run!"))
			self.logger.info("[CC-RUN] - Path finished!")
			task_paths_counter += 1

		self.logger.info("[CC-RUN] - >> CyberCaptain finished!")

	def get_all_task_paths(self, config, modules_conf):
		"""
		This method checks the defined script config file and returns the defined paths.
		Paths are found with finding final steps (target not linked to any src) and bubble up from them.

		**Parameters**: 
		config: path
			a path to the script config containing all tasks
		modulesConfig: path
			a path to the modules config file containing all modules, defaults to DEFAULT_MODULES_CONFIG_PATH

		**Returns**: 
			``list`` containing all task paths in reversed order (bottom to top).
		"""
		task_paths = []
		final_steps = self.get_final_steps(config, modules_conf)

		for final_step in final_steps:
			curr_task_name = final_step
			task_path = [curr_task_name]
			while self.get_config_name_for_attribute(config, 'target', config[curr_task_name].get("src",None), self.is_wc_src_module(curr_task_name, modules_conf)):
				next_task_name = self.get_config_name_for_attribute(config, 'target', config[curr_task_name]['src'], self.is_wc_src_module(curr_task_name, modules_conf))
				task_path.append(next_task_name)
				curr_task_name = next_task_name
			task_paths.append(task_path)
		return task_paths

	def check_depends_on_file_and_not_exists(self, config, n, module):
		"""
		This method checks if a given module offers the functionality to depends_on_file and if the depending file exists.
		Is used by the processing modules to support file generation of other paths (and wait for them if not executing in order).

		**Parameters**: 
		config: dict
			the loaded script config file.
		n: str
			the current running task name.
		module: obj
			the current running, preconfigured and to be checked module.

		**Returns**:
			``str`` if module offers depends_on_file func and the depending file is not existing yet..
			``False`` if module does not offer any depends_on_file functionality or depending file is existing. 
		"""
		if "depends_on_file" in dir(module):
			dep_attribute = module.depends_on_file()
			if dep_attribute:
				if not fileExists(config[n][dep_attribute]):
					return config[n][dep_attribute]
				else:
					self.logger.info("[CC-RUN] - Depending file (%s) for task %s is ready!" % (config[n][dep_attribute], n))
					return False
		return False

	def check_and_get_additional_paths(self, task_paths, task_paths_counter, config, task_name, module):
		"""
		This method checks if a given module offers the functionality to inject_additional_tasks and if additional tasks are available.
		Is used by the store modules to check if datasets are missing and have not been processed yet.

		**Parameters**: 
		task_paths: list
			the list of the initial loaded task_paths. Used to get the current running path from.
		task_paths_counter: int
			the current number of the running task. Used to get the current path from task_paths.
		config: dict
			the loaded script config file.
		task_name: str
			the current running task name.
		module: obj
			the current running, preconfigured and to be checked module.

		**Returns**:
			``list`` containing all additional task paths to be appended to the task paths currently running.
			``None`` if module does not offer any inject_additional_tasks functionality or no additional tasks available. 
		"""
		# Issue 72 - inject_additional_tasks - RESERVED function name
		if "inject_additional_tasks" in dir(module):
			additional_paths = []
			
			additional_tasks = module.inject_additional_tasks() # List mit [{"attributes":{KWRGS_OF_THE_STORE_CLASS}, "identifier": "IDENTIFIER"}]
			if additional_tasks:
				self.logger.info("[CC-RUN] - %d additional path(s) for %s were found - appending them now!" % (len(additional_tasks), task_name))
				self.logger.debug("[CC-RUN] - Current path is %s" % str(task_paths[task_paths_counter]))
				self.logger.debug("[CC-RUN] - Current task is %s" % task_name)

				for add_task in additional_tasks:
					additional_path = []

					# Append new store task (main) with the returned attributes and new name with identifier added
					new_main_tasknamne = self.append_str_to_taskname(task_name, add_task["identifier"])
					
					config[new_main_tasknamne] = add_task["attributes"]
					additional_path.append(new_main_tasknamne)

					for t in task_paths[task_paths_counter]: # For every further task step create a new task with the specific additional task identifier
						if t == task_name: continue # This is our current task where we started to inject which gets a special config which is already appended
						
						# Update src
						updated_task_conf = config[t].copy() # original task config
						updated_task_conf["src"] = append_str_to_filename(config[t]["src"], add_task["identifier"]) # add identifier to the old src as new
						updated_task_conf["target"] = append_str_to_filename(config[t]["target"], add_task["identifier"])  # add identifier to old target as new

						# Update target
						new_tasknamne = self.append_str_to_taskname(t, add_task["identifier"])
						config[new_tasknamne] = updated_task_conf # add new task to config with identifier added
						additional_path.append(new_tasknamne)
				
					additional_paths.append(list(reversed(additional_path))) # Add the new path to the additional_paths - needs to be reversed as run algo reverses the list again to start from top to bottom

				return additional_paths
			else:
				self.logger.debug("[CC-RUN] - Module task [%s] did not return any additional paths" % task_name)
				return None
		else:
			self.logger.debug("[CC-RUN] - Module task [%s] does not offer additional paths" % task_name)
			return None

	def append_project_root_path_walker(self, section, key):
		"""
		This method is used for the configobj walker to go through the whole file (section and keys) and append the project root paths to target and sources.
		Currently appended on keys: src, target, joinwith

		**Parameters**: 
		section: str
			the current section given by the configobj walker.
		key: str
			the current key given by the configobj walker.
		"""
		if key in ["src", "target", "joinwith"] and "projectRoot" in self.loaded_conf:
			val = section[key]

			# Needs to be checked if its an absolute path, aso two joined absolute paths result in the second absolut path only
			if os.path.isabs(val): raise KeyError("The src or target value '%s' is an absolute path. Please use a relative path to the rootPath!" % val)
				
			section[key] = os.path.join(self.loaded_conf["projectRoot"], val)

	def replace_placeholders_walker(self, section, key):
		"""
		This method is used for the configobj walker to go through the whole file (section and keys) and replaces configured placeholders at the right place.

		**Parameters**: 
		section: str
			the current section given by the configobj walker.
		key: str
			the current key given by the configobj walker.
		"""
		# Replace Placeholders
		val = section[key]
		if isinstance(val, (tuple, list, dict)):
			pass
		else:
			for match in self.get_placeholder_matches(val):
				m = match.group(1)
				if m.lower() == "currentdate":
					val = val.replace("{{"+ m +"}}", time.strftime("%d%m%Y"))
				elif m.lower() == "currentdatetime":
					val = val.replace("{{"+ m +"}}", time.strftime("%d%m%Y-%H%M%S"))
				else:
					if self.cphs and m in self.cphs:
						val = val.replace("{{"+ m +"}}", self.cphs[m])
					else:
						raise KeyError("The CyberCaptain config file contains undefined (%s) placeholders [-cp]" % m)
			section[key] = val

	def get_placeholder_matches(self, val):
		"""
		This method is used to match a string for placeholders '{{xxx}}'.

		**Parameters**: 
		val: str
			the string to match for placeholders.

		**Returns**:
			``list`` containing all matches.
		"""
		return re.finditer(r'\{{([^\}]*)\}}', val)

	def get_class_by_module_conf_key(self, module_conf):
		"""
		This method loads the class for a given module conf key which is defined in the module config.

		**Parameters**: 
		module_conf: list
			contains on index 0 the path to the module and on index 1 the class name.

		**Returns**: 
			``cybercaptainClass`` loaded from the correct module.
		"""
		return getattr(importlib.import_module(module_conf[0]), module_conf[1])

	def get_config_name_for_attribute(self, config, attribute, match, match_is_wildcard):
		"""
		This method returns the script config keyname where a wanted attribute is matching 
		(E.g. looking for a module with SRC=XY will return the section key ``processing_clean CLEAN1`` if that is the section where the SRC is XY)

		**Parameters**: 
		config: configObj
			is the loaded script config configObj.
		attribute: str
			the attribute we are looking for in all the script configs.
		match: str
			to what the attribute should match.
		match_is_wildcard: bool
			if its a wildcard we need to read the match as a wildcard to find matching stuff.

		**Returns**: 
      		the section key e.g. ``processing_clean CLEAN1`` if found and ``None``if not found.
		"""
		for s in config.sections:
			if match_is_wildcard and (config[s][attribute] and fnmatch.fnmatch(config[s][attribute], match)):
				return s
			elif config[s][attribute] and config[s][attribute] == match:
				return s
		return None

	def get_final_steps(self, config, modules_conf):
		"""
		This method returns a list of all tasks in the script config file which have a TARGET which is not used as a SRC anywhere.

		**Parameters**: 
		config: configObj
			is the loaded script config configObj.
		modules_conf: configObj
			is the loaded modules config configObj.

		**Returns**: 
      		a list containing all final step script config keys e.g. ``["visualization_bar V1","visualization_line V2"]``.
		"""
		# Get final steps of a config (targets are not used as source anywhere)
		final_steps = []
		all_sources = [config[s]["src"] for s in config.sections if "src" in config[s]]
		all_targets = [config[s]["target"] for s in config.sections]
		
		for s in config.sections:
			if (config[s]["target"] not in all_sources): # Check if the target is not in any of the sources (last task in a config)
				# Additional wildcard checks
				# 1st If: Module is a wildcard src module and its source matches any of the targets in the script config
				# 2nd If: Check if the target is not used in any other module with as a src with a wildcard pattern
				if ((s.split(" ")[0].lower() in modules_conf["wildcard_src_modules"]) and (len(fnmatch.filter(all_targets, config[s]["src"])) > 0))\
					or not self.target_used_as_wc_src(all_sources, config[s]["target"]): 
						final_steps.append(s)

		return final_steps

	def paths_have_file_extensions(self, paths):
		"""
		Method checks if all paths given have a file extension.
		Depending on use case this is needed (for example if we get missing datasets and use injection)

		**Parameters**: 
		paths: list
			list containing paths to check.

		**Returns**: 
      		``True`` if all paths have a file extension.
			``False`` if not all paths have a file extension.
		"""
		for p in paths:
			if get_file_extension(p) == '': return False
		return True

	def target_used_as_wc_src(self, all_sources, target):
		"""
		This method returns True if a given target matches a wildcard source anywhere in the config.
		Needed regarding the run algo as if there is a wildcard source, the target <-> source can't be directly matched,
		so that fnmatch is needed to look for sources which match a specific target and do not duplicate paths.

		**Parameters**: 
		all_sources: list
			a list of all detected sources.
		target: str
			a string of the target url name.

		**Returns**: 
      		True if the given target is used anywhere from a wildcard source and False if target is not used anywhere anymore.
		"""
		for s in all_sources:
			if fnmatch.fnmatch(target, s): return True
		return False


	def is_wc_src_module(self, module_name, modules_conf): 
		"""
		This method returns a boolean if the module name is registered as a wildcard src module in the module config.
		This is important for checking wildcards in the SRC definition.

		**Parameters**: 
		module_name: str
			the key of the section containing the module name.
		modules_conf: configObj
			is the loaded modules config configObj.

		**Returns**: 
      		``True``if it's a wildcard module and ``False`` if it is not a wildcard module.
		"""
		# Issa wildcard src module
		return (module_name.split(" ")[0] in modules_conf["wildcard_src_modules"])


	def checksum_check(self, project_name, project_path, ccs_path):
		"""
		This method returns a boolean if the checksum of the script config file matches the previous run or if it has changed.
		The script config files are matched by their projectName - if the projectname changes the checksum will not be checked to the previous run as a new KVStore is created.
		Can have impact on the KV store if things in the script config have changed and the modules access the old KV-Store.

		**Returns**: 
      		``True``if the checksum is new or the same, ``False`` if the checksum has changed.
		"""
		content = ""
		if os.path.isfile(ccs_path):
			store = kv_store(dir_name=project_path, file_name=project_name)
			with open(ccs_path,'r') as f: content = f.read()

			curr_checksum = make_sha1(content)

			if self.overwritechecksum:
				self.logger.warning("[CC-RUN] - Checksum overwritting flag set, set from  %s to %s" % (store.get("projectChecksum"), curr_checksum))
				store.put(key="projectChecksum", value=curr_checksum, force=True)

			prev_checksum = store.get("projectChecksum")

			if prev_checksum is not None and prev_checksum != curr_checksum:
				self.logger.warning("[CC-RUN] - The project script config checksum does not match (Old: %s - New: %s)" %(prev_checksum, curr_checksum))
				if not self.ignoreChecksum: return False
				self.logger.warning("[CC-RUN] - We are ignoring the checksum check!")
			else:
				store.put(key="projectChecksum", value=curr_checksum, force=True)
			self.logger.info("[CC-RUN] - Script config checksum check finished!")
			return True
		else:
			raise FileNotFoundError("Please define an existing CyberCaptain-Script-Config file!")

	def append_str_to_taskname(self, module_taskname, str_to_append):
		"""
		Appends a given string to a taskname [module_name taskname ADDITIONALSTR].
		Used to inject additional tasks with a different name.

		**Parameters**:
			module_taskname : str
				The module and taskname from the script config.
			str_to_append: str
				The str to append.

		**Returns**:
			`str` module_taskname with the given str appended.
		"""
		s_module, s_name, *identifier = module_taskname.split(" ")
		return "{s_module} {s_name} {appended}".format(s_module=s_module, s_name=s_name, appended=str_to_append)

	def get_log_location(self):
		"""
		Returns the location to write the log to.
		If config obj is valid and projectroot defined it will be written to there.
		If something wrong regarding the script config it will be only written to the stdout.

		**Returns**:
			`str` log location in the defined projectroot or current executing place.
			`None` if there is no projectRoot defined or script config is not existing/readable.
		"""
		if self.config and fileExists(self.config):
			try:
				loaded_conf = ConfigObj(self.config)
				loaded_conf.walk(self.replace_placeholders_walker)
				if "projectRoot" in loaded_conf and os.path.isabs(loaded_conf['projectRoot']) and os.path.isdir(loaded_conf['projectRoot']):
					return loaded_conf['projectRoot']
			except:
				pass
		return None


def create_parser():
	"""
	This method creates the parser which is used to parse inputs for CyberCaptain.

	**Returns**:
		``ArgumentParser`` with configured CC-Params.
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--config", help="cybercaptain config file location", dest='config')
	parser.add_argument("-mc", "--modulesconfig", help="cybercaptain modules config file location")
	parser.add_argument("-v", "--validate", help="validate config file and do not execute", action="store_true")
	parser.add_argument("-cp", "--customplaceholders", help="define and add a custom placeholder to the config", action='append', type=lambda kv: kv.split("="), dest='customplaceholders')
	parser.add_argument("-d", "--debug", help="set verbosity to debug and also redirect log output to stdout", action="store_true")
	parser.add_argument("--overwritechecksum", help="overwrite the script config checksum if changed", action="store_true")
	parser.add_argument("--ignorechecksum", help="ignore the script config checksum check and continue on own risk", action="store_true")
	parser.add_argument("-pv", "--pathvisualize", help="visualizes the path and generates visualized html file", action="store_true")
	parser.add_argument('others', nargs='*')  # Everything else - Added regarding pyb unittest arguments which will fail otherwise
	return parser

def main(args):
	"""
	This is the main method which will run if the script gets executed via CLI.

	**CLI Paramateres**: 
	-c:
		the path to the wanted script config file.
	--config:
		see ``-c``.
	-mc:
		OPTIONAL: the wanted module config file, has a default value to ``modules.ccc``.
	--modilesconfig:
		see ``-mc``.
	-v:
		if only a validation is needed without any run.
	--validate:
		see ``-v``.
	-cp:
		to define and fill in the custom placeholders in the script config file e.g. ``-cp xy=1``.
	--customplaceholders:
		see ``-cp``.
	-d:
		to define if logging output should also be redirected to the stdout and set verbosity to debugs.
	--debug:
		see ``-d``.
	--overwritechecksum:
		overwrite the script config checksum if changed.
		An existing KV store could contain wrong data if the config for a module has been changed which relies on the KV-Store.
		Recommended usage: If things in the script configuration were changed, we recommend to "reset" the project by deleting all files in the projectRoot
			(including the KV-Store) to minimize problems and issues.
	--ignorechecksum:
		ignore the script config checksum check and continue on own risk. 
		An existing KV store could contain wrong data if the config for a module has been changed which relies on the KV-Store.
		Recommended usage: If things in the script configuration were changed, we recommend to "reset" the project by deleting all files in the projectRoot
			(including the KV-Store) to minimize problems and issues.
	-pv:
		if only the path should be visualized. outputs the path visualized in a html file.
	--pathvisualize:
		see ``-pv``.
	"""

	if not args.config:
		raise Exception("Please define the config file location [-c|--config]")

	# Issue 32, restructured modules and add them via a config
	modules_config = DEFAULT_MODULES_CONFIG_PATH
	if args.modulesconfig: modules_config = args.modulesconfig

	# Issue 25, added placeholder replacer
	customPlaceholders = None
	if args.customplaceholders:
		customPlaceholders = dict(args.customplaceholders)

	return CyberCaptain(config=args.config, modulesConfig=modules_config, validate=args.validate, customplaceholders=customPlaceholders, debug=args.debug, overwritechecksum=args.overwritechecksum, ignoreChecksum=args.ignorechecksum, pathVisualize=args.pathvisualize)

if __name__ == "__main__":
	main(create_parser().parse_args(sys.argv[1:]))