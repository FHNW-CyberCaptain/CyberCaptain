"""
This module contains the store shodan class.
"""
import shodan
import json
from datetime import datetime
from cybercaptain.store.base import store_base
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.utils.helpers import str2bool, append_str_to_filename
from cybercaptain.utils.jsonFileHandler import json_file_writer
from cybercaptain.utils.kvStore import kv_store


class store_shodan(store_base):
	"""
	The shodan module ensures a correct implementation of the shodan.io api interface and makes it easy to download shodan datasets.
	Shodan module supports two lookup types: ip_lookup & search_query.

	More information can be found on: http://shodan.readthedocs.io/en/latest/api.html

	**Important**: A commercial or EDU shodan account is needed to have the full functionality. We take no responsiblity to issues related to a free account.

	**Parameters**:
		kwargs:
			contains a dictionary of all attributes.

	**Script Attributes**:
		apiKey : str
			Define the API key received from shodan which is used to access the data via API.
		type : str
			Define the wanted lookup type [ip_lookup|search_query].
		minify : bool
			True to only return the list of ports and the general host information, no banners.
	**Script Attributes [ip_lookup]**:
		ip	: str
			Define the IP-Address to lookup (E.g. '1.1.1.1')
		port : int
			Define the port trying to get shodan data from (shodan has to have data for this port - e.g. 80)
		getByDatasetTs : str
			Get the lookup data by a specific defined timestamp.
		getByLatest : bool
			Get the lookup data by the latest available data.
		getMissingDatasets : bool
			Define if the run should be checked for missing datasets happened between last scan and new scan which have not been processed yet.
		getAllMissingDatasets : bool
			Define if the run should get all missing datasets from the beginning which have not been processed yet.
	**Script Attributes [search_query]**:
		query : str
			Define the shodan search query according to the shodan docs.
		limit : int
			Define the amount of wanted results (Important to save shodan account credits).
		retries : int
			Define the amount of retries in case of a timeout.
	"""
	def __init__(self, **kwargs):
		kwargs["src"] = "." # src-less module

		super().__init__(**kwargs)
		self.validate(kwargs)

		self.apiKey = kwargs.get("apiKey")
		self.type = kwargs.get("type")
		self.minify = str2bool(kwargs.get("minify"))
		# ip_lookup
		self.ip = kwargs.get("ip")
		self.port = int(kwargs.get("port","0"))
		self.get_by_latest = str2bool(kwargs.get("getByLatest"))
		self.get_by_dataset_ts = kwargs.get("getByDatasetTs")
		self.get_missing_sets = str2bool(kwargs.get("getMissingDatasets")) # Inject additional paths
		self.get_all_missing_sets = str2bool(kwargs.get("getAllMissingDatasets"))
		# search_query
		self.query = kwargs.get("query")
		self.limit = int(kwargs.get("limit","1"))
		self.retries = int(kwargs.get("retries","5"))

		# KV-Store Init
		self.kv_store = kv_store(self.projectRoot, self.projectName)

		# Save current configs - Used for missingDatasets
		self.kwargs = kwargs

	def run(self):
		"""
		Runs the shodan algorythm.

		**Returns**:
			``True`` if the run method has run succesful. ``False`` if something did not work out.
		"""
		self.cc_log("INFO", "Data Store Shodan: Started Run")
		try: 
			if self.type == "ip_lookup":
				return self.run_shodan_ip_lookup()
			elif self.type == "search_query":
				return self.run_shodan_search_query()
			else:
				self.cc_log("ERROR", "Failed to run shodan module as no valid type was found (ip_lookup, search_query)!")
				self.cc_log("INFO", "Data Store Shodan: Finished Run With Error")
				return False
		except Exception as e:
			self.cc_log("ERROR", "Failed to run the shodan module (%s)" % e)
			self.cc_log("ERROR", "Data Store Shodan: Finished Run With Error")
			return False
	
		return False

	def run_shodan_ip_lookup(self):
		"""
		Runs the shodan api ip lookup and gets the most recent one.

		**Returns**:
			``True`` if the ip and port lookup was successfull and data written.
			``False`` if the lookup failed.
		"""
		self.cc_log("INFO", "Data Store Shodan: Started IP Lookup For %s" % self.ip)

		if self.get_by_latest:
			lookup_data = self.get_ip_lookup_data_by_latest()
		elif self.get_by_dataset_ts:
			lookup_data = self.get_ip_lookup_data_by_dataset_ts(self.get_by_dataset_ts)
		else:
			self.cc_log("ERROR", "No valid ip lookup option was defined.")

		if not lookup_data: 
			self.cc_log("INFO", 'Data Store Shodan: Finished Run With No Data')
			return False

		if self.process_ip_lookup_data(lookup_data):
			self.cc_log("INFO", 'Data Store Shodan: Finished Run Success')
			return True
	
		self.cc_log("WARNING", 'Data Store Shodan: Finished Run With Skip or Error')			
		return False

	def get_ip_lookup_data_by_latest(self):
		"""
		Get the shodan ip lookup data via latest available timestamp.

		**Returns**:
			``{DATASET}`` if the ip lookup did find the newest dataset.
			``None`` if the port is not available in the scans.
		"""
		self.cc_log("INFO", "Get shodan ip lookup data by latest")
		s_api = shodan.Shodan(self.apiKey)
		host_info = s_api.host(self.ip, minify=self.minify)

		if not self.is_port_in_available_ports(host_info): return None

		for d in host_info["data"]:
			if "port" in d and d["port"] is self.port:
				self.cc_log("INFO", 'Found banner data for port [%s] with timestamp [%s]' % (self.port, d["timestamp"]))
				return d

		self.cc_log("ERROR", "No shodan data was found for the available port %s" % (self.port))
		return None

	def get_ip_lookup_data_by_dataset_ts(self, dataset_ts):
		"""
		Get the shodan ip lookup data via a defined dataset timestamp.

		**Parameters**:
			dataset_ts : str
				the dataset timestamp to look for in the host info results.

		**Returns**:
			``{DATASET}`` if the ip lookup did find the defined TS and port.
			``None`` if the port is not available in the scans or not data with the TS was found.
		"""
		self.cc_log("INFO", "Get shodan ip lookup data by dataset timestamp %s" % (dataset_ts))
		s_api = shodan.Shodan(self.apiKey)
		host_info = s_api.host(self.ip, history=True, minify=self.minify)

		if not self.is_port_in_available_ports(host_info): return None

		for d in host_info["data"]:
			if ("port" in d and d["port"] is self.port) and ("timestamp" in d and d["timestamp"] == dataset_ts):
				self.cc_log("INFO", 'Found banner data for port [%s] with timestamp [%s]' % (self.port, d["timestamp"]))
				return d

		self.cc_log("ERROR", "No shodan data was found for the available port %s with timestamp %s" % (self.port, dataset_ts))
		return None

	def process_ip_lookup_data(self, lookup_data):
		"""
		Writes an ip lookup dataset to the target file if not already processed and sets it as processed after.

		**Parameters**:
			lookup_data : dict
				single ip lookup dataset received via shodan api.

		**Returns**:
			``True`` if the ip lookup data was written.
			``False`` if the lookup was already processed and not written.
		"""
		data_ts = lookup_data["timestamp"]

		# Check if we did process the timestamp before but with another targetname
		processed_ts = self.kv_store.get("processed_ts", section=self.moduleName)
		if not processed_ts: processed_ts = []

		if data_ts not in processed_ts:
			self.cc_log("INFO", 'Banner data for TS %s has not been processed yet' % (data_ts))

			json_fw = json_file_writer(self.target)
			json_fw.writeRecord(lookup_data)
			json_fw.close()

			processed_ts.append(data_ts)
			self.kv_store.put("processed_ts", processed_ts, section=self.moduleName, force=True)

			# Save the newest processed timestamp to be able to tell times between last run and the current run
			newest_processed_ts = self.kv_store.get("newest_processed_ts", section=self.moduleName)
			if not newest_processed_ts or self.shodan_ts_is_newer(data_ts, newest_processed_ts):
				self.kv_store.put("newest_processed_ts", data_ts, section=self.moduleName, force=True)

			# Save the target file for an explicit timestamp to be able to tell the file if it was already processed
			self.kv_store.put(data_ts, self.target, section=self.moduleName, force=True)

			return True
		else:
			original_target = self.kv_store.get(data_ts, section=self.moduleName)
			self.cc_log("WARNING", "Dataset with the TS %s has been already processed with the target %s - skip rest of the path!" % (data_ts, original_target))
			return False

	def run_shodan_search_query(self):
		"""
		Runs the shodan api search query lookup.

		**Returns**:
			``True`` if the search query lookup was successfull and the data written.
			``False`` if the lookup failed.
		"""
		self.cc_log("INFO", "Data Store Shodan: Started Search Query Lookup With Query '%s'" % self.query)

		s_api = shodan.Shodan(self.apiKey)
		json_fw = json_file_writer(self.target)

		counter = 0
		for banner in s_api.search_cursor(self.query, minify=self.minify, retries=self.retries):
			json_fw.writeRecord(banner)

			counter += 1
			self.cc_log("DEBUG", "Data amount: %s!" % (counter))
			if counter >= self.limit:
				break

		json_fw.close()
		if counter > 0:
			self.cc_log("INFO", "A total of %s banner data was downloaded!" % (counter))
			return True

		self.cc_log("WARNING", "No data was downloaded via search cursor lookup!")
		return False


	def shodan_ts_is_newer(self, d1, d2):
		"""
		Compares two shodan timestamps if d1 > d2 (d1 newer than d2)
		Timestamp example: 2018-06-20T23:29:09.514418

		**Parameters**:
			d1 : str
				First shodan timestamp string to compare.
			d2 : str
				Second shodan timestamp string to compare.

		**Returns**:
			``True`` if d1 newer than d2.
			``False`` if d2 newer than d1.
		"""
		shodan_ts_parser = "%Y-%m-%dT%H:%M:%S.%f"
		datetime1 = datetime.strptime(d1, shodan_ts_parser)
		datetime2 = datetime.strptime(d2, shodan_ts_parser)
		return datetime1 > datetime2

	def is_port_in_available_ports(self, host_info):
		"""
		Simple internal check used to check if the wanted port is available in the ip lookup scan.

		**Parameters**:
			host_info : dict
				host info dict received via shodan api.

		**Returns**:
			``True`` if port was scanned and available.
			``False`` if port was not scanned and not available.
		"""
		self.cc_log("INFO", "Available ports are %s" % host_info['ports'])
		if self.port in host_info['ports']: return True
		self.cc_log("ERROR", "No shodan lookup data available for port %s and IP %s" % (self.port, self.ip))
		return False

	def validate(self, kwargs):
		"""
		Validates all arguments for the shodan module.

		**Parameters**:
			kwargs : dict
				contains a dictionary of all attributes.
		"""
		super().validate(kwargs)
		self.cc_log("INFO", "Data Store Shodan: Started Validation")
		if not kwargs.get("apiKey"): raise ValidationError(self, ["apiKey"], "Parameter cannot be empty!")
		if not kwargs.get("type"): raise ValidationError(self, ["type"], "Parameter cannot be empty!")
		if kwargs.get("type") != "ip_lookup" and kwargs.get("type") != "search_query": raise ValidationError(self, ["type"], "Type has to be 'ip_lookup' or 'search_query'")


		if kwargs.get("type") == "ip_lookup":
			if not kwargs.get("ip"): raise ValidationError(self, ["ip"], "Parameter cannot be empty!")
			if not kwargs.get("port"): raise ValidationError(self, ["port"], "Parameter cannot be empty!")

			if not kwargs.get("getByLatest") and not kwargs.get("getByDatasetTs"): raise ValidationError(self, ["getByLatest","getByDatasetTs"], "One of them has to be defined!")
			if kwargs.get("getMissingDatasets") and kwargs.get("getAllMissingDatasets"): raise ValidationError(self, ["getMissingDatasets", "getAllMissingDatasets"], "Please only use one!")

		if kwargs.get("type") == "search_query":
			if not kwargs.get("query"): raise ValidationError(self, ["query"], "Parameter cannot be empty!")
			if not kwargs.get("limit"): raise ValidationError(self, ["limit"], "Parameter cannot be empty!")
			if not kwargs.get("retries"): raise ValidationError(self, ["retries"], "Parameter cannot be empty!")
			if kwargs.get("getMissingDatasets"): raise ValidationError(self, ["getMissingDatasets"], "Parameter only usable for type 'ip_lookup'!")
			if kwargs.get("getAllMissingDatasets"): raise ValidationError(self, ["getAllMissingDatasets"], "Parameter only usable for type 'ip_lookup'!")

		self.cc_log("INFO", "Data Store Censys: Finished Validation")

	def inject_additional_tasks(self):
		"""
		Overwrite base method 'inject_additional_tasks'.

		Checks for additional and not yet processed results from the last run if lookup type is 'ip_lookup' and 'getMissingDatasets' = True .
		Checks for additional and not yet processed results from the first dataset the API offers if lookup type is 'ip_lookup' and 'getAllMissingDatasets' = True .
		
		Attention: The basic shodan account will not be allowed to do these calls!

		**Returns**:
			``list`` with additional tasks. List contains dict {}
				-> Dict with "attributes" containing the modules adapted kwargs and "identifier" containing a specific identifier for the new task.
			``False`` if no additional tasks need to be injected.
		"""
		if (self.get_missing_sets or self.get_all_missing_sets) and self.type == "ip_lookup":
			mode = "GET ALL MISSING DATASETS" if self.get_all_missing_sets else "GET MISSING DATASETS BETWEEN LAST RUN AND NEWEST"
			self.cc_log("INFO", "Data Store Shodan: Looking for missing datasets for %s and port %s in mode [%s]" % (self.ip, self.port, mode))

			s_api = shodan.Shodan(self.apiKey)
			host_info = s_api.host(self.ip, history=True, minify=self.minify)

			if not self.is_port_in_available_ports(host_info): return False

			newest_processed_ts = self.kv_store.get("newest_processed_ts", section=self.moduleName)
			processed_ts = self.kv_store.get("processed_ts", section=self.moduleName)
			if not processed_ts: processed_ts = []
			
			additional_tasks = []
			for hi in host_info["data"]:
				# Checks if wanted port is available
				# If option all missing datasets is set, check if timestamp does not exist in the processed_ts list and then append
				# If option just to get missing sets from last run to the current is set, check if we have a last run and if the timestamp is newer than the last run and then append
				if ("port" in hi and hi["port"] is self.port) \
					and ((self.get_all_missing_sets and hi["timestamp"] not in processed_ts) \
						or (self.get_missing_sets and newest_processed_ts and self.shodan_ts_is_newer(hi["timestamp"], newest_processed_ts))):
					
					timestamp_cleaned = hi["timestamp"].replace(":","").split(".")[0]

					changed_kwargs = self.kwargs.copy()
					changed_kwargs.pop("getMissingDatasets", None) 		# Make sure missing datasets not called again on new task
					changed_kwargs.pop("getAllMissingDatasets", None)
					changed_kwargs.pop("getByLatest", None) 			# Remove get by latest as we get additional data direct via timestamp
					changed_kwargs["getByDatasetTs"] = hi["timestamp"] 	# Define timestamp for the missing dataset
					changed_kwargs["target"] = append_str_to_filename(self.target, timestamp_cleaned)

					additional_tasks.append({"attributes": changed_kwargs, "identifier": timestamp_cleaned})

			self.cc_log("DEBUG", "Total found datasets: %d" % len(host_info["data"]))
			self.cc_log("DEBUG", "Additional not processed/missed datasets: %d" % len(additional_tasks))

			# If the first element in additional tasks has a newer timestamp than the last -> Reverse the list so it gets processed from old to new
			if len(additional_tasks) >= 2:
				if self.shodan_ts_is_newer(additional_tasks[0]["attributes"]["getByDatasetTs"], additional_tasks[-1]["attributes"]["getByDatasetTs"]):
					additional_tasks = list(reversed(additional_tasks))

			return additional_tasks

		return False
