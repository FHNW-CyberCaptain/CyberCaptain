"""
This module contains the store censys class.
"""
import json
import requests
import math
import lz4.frame
import os
import datetime
import censys.data
import re
import shutil
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.utils.helpers import str2bool, append_str_to_filename
from cybercaptain.utils.kvStore import kv_store
from cybercaptain.store.base import store_base

DEFAULT_CHUNK_SIZE_DOWNLOAD = 2048
DEFAULT_CHUNK_SIZE_DECOMPRESS = 2048

HTTP_CODE_NOTVALID_THRESHOLD = 400 # If http response has status >= 400 means it failed

class store_censys(store_base):
	"""
	The censys module ensures a correct implementation of the censys.io api interface and makes it easy to download censys datasets.
	Censys module expects the data do be .LZ4 compressed via API and direct URL.
	**Important**: A commercial or research censys account is needed to have the full functionality like history. 

	**Parameters**:
		kwargs:
			contains a dictionary of all attributes.

	**Script Attributes**:
		apiSecret:
			The API credentials Secret received from censys.io (Found on https://censys.io/account/api).
		apiId:
			The API credentials ID received from censys.io (Found on https://censys.io/account/api).
		seriesId:
			Define the wanted seriesId (Can be found on scans.io) - e.g. '22-ssh-banner-full_ipv4'.
		fileId:
			If we are getting files viaApi and we have to define which file we want to obtain from scans.io / censys.io
			E.g. zgrab-results
		getByLatest:
			Define if we do not define datasetId or timestampId ourselves but go for the latest dataset.
		getByDate:
			Get the data by a specific date. If there is no file found, skip 
		getByDatasetId:
			If we are not looking for the latest dataset, datasets can be selected directly via datasetId of the respective dataset in the defined series (seriesId) - e.g. '20150930T0056'.
			This value has to be looked for manually via their api. We recommend to use getLatest to not worry about this too much.
		getMissingDatasets : bool
			Define if the run should be checked for missing datasets happened between last scan and new scan which have not been processed yet.
		getAllMissingDatasets : bool
			Define if the run should get all missing datasets from the beginning which have not been processed yet.
		chunkSizeDownload:
			Set a custom download chunk size (Default: 2048)
		chunkSizeDecomp:
			Set a custom decompress chunk size (Default: 2048)
	"""
	def __init__(self, **kwargs):
		kwargs["src"] = "." # src-less module

		super().__init__(**kwargs)
		self.validate(kwargs)

		self.api_id = kwargs.get("apiId")
		self.api_secret = kwargs.get("apiSecret")
		self.series_id = kwargs.get("seriesId")
		self.file_id = kwargs.get("fileId")

		self.get_by_latest = str2bool(kwargs.get("getByLatest"))
		self.get_by_date = kwargs.get("getByDate")
		self.get_by_datasetId = kwargs.get("getByDatasetId")

		self.get_missing_sets = str2bool(kwargs.get("getMissingDatasets")) # Inject additional paths
		self.get_all_missing_sets = str2bool(kwargs.get("getAllMissingDatasets"))

		# KV-Store Init
		self.kv_store = kv_store(self.projectRoot, self.projectName)

		# Default Chunk Sizes
		if kwargs.get("chunkSizeDownload"):
			self.chunk_size_dl = kwargs.get("chunkSizeDownload")
		else:
			self.chunk_size_dl = DEFAULT_CHUNK_SIZE_DOWNLOAD

		if kwargs.get("chunkSizeDecomp"):
			self.chunk_size_dec = kwargs.get("chunkSizeDecomp")
		else:
			self.chunk_size_dec = DEFAULT_CHUNK_SIZE_DECOMPRESS

		# Save current configs - Used for missingDatasets
		self.kwargs = kwargs

	def run(self):
		"""
		Runs the censys algorythm.

		**Returns**:
			``True`` if the run method has run succesful. ``False`` if something did not work out.
		"""
		self.cc_log("INFO", "Data Store Censys: Started")

		dataset_wanted_file_url = None
		dataset_id = None
		# Get the data via api
		try:
			c = censys.data.CensysData(api_id=self.api_id, api_secret=self.api_secret)
			if self.get_by_latest: # getByLatest Flag Set To True
				dataset_id, dataset_wanted_file_url = self.via_api_get_by_latest(c, self.series_id)
			elif self.get_by_date: # getByDate Flag Is Set To True
				dataset_id, dataset_wanted_file_url = self.via_api_get_by_date(c, self.series_id, self.get_by_date)
			elif self.get_by_datasetId: # getByDatasetId Flag Is Set To True
				dataset_id, dataset_wanted_file_url = self.via_api_get_by_datasetId(c, self.series_id, self.get_by_datasetId)
			else:
				self.cc_log("ERROR", "Failed to run censys module viaAPI as no valid method was found (getByLatest, getByDate, getByDatasetId)!")
				return False
		except Exception as e: # Possibly a generic error (wrong credentials?)
			self.cc_log("ERROR", "Failed to run the censys module viaAPI (%s)" % e)
			return False
			
		if not dataset_wanted_file_url:
			self.cc_log("WARNING", "Failed to get a censys download url - skip the path. Please recheck if intended.")
			return False

		# Check if we did process the id before but with another targetname
		processed_ids = self.kv_store.get("processed_ids", section=self.moduleName)
		if not processed_ids: processed_ids = []

		if dataset_id and dataset_id in processed_ids:
			original_target = self.kv_store.get(dataset_id, section=self.moduleName)
			self.cc_log("WARNING", "Dataset with the ID %s has been already processed with the target %s - skip rest of the path!" % (dataset_id, original_target))
			return False

		# Download and decompress the censys file
		self.download_file(dataset_wanted_file_url, self.target+".downloaded", self.chunk_size_dl)
		self.decompress_lz4(self.target+".downloaded", self.target+".tmp", self.chunk_size_dec)
		shutil.move(self.target+".tmp",self.target)

		if dataset_id:
			processed_ids.append(dataset_id)
			self.kv_store.put("processed_ids", processed_ids, section=self.moduleName, force=True)

			# Save the newest processed ID to be able to tell times between last run and the current run
			newest_processed_id = self.kv_store.get("newest_processed_id", section=self.moduleName)
			if not newest_processed_id or self.censys_id_is_newer(dataset_id, newest_processed_id):
				self.kv_store.put("newest_processed_id", dataset_id, section=self.moduleName, force=True)

			# Save the target file for an explicit ID to be able to tell the file if it was already processed
			self.kv_store.put(dataset_id, self.target, section=self.moduleName, force=True)

		self.cc_log("INFO", "Data Store Censys: Finished")
		return True

	def via_api_get_by_latest(self, censys_data, series_id):
		"""
		Get the latest data via api.

		**Returns**:
			(``str``, ``str``) pair containing unique identifier and the compressed download path if found. 
			``None`` if latest dataset was not found or failed.
		"""
		series = self.censys_api_view_series(censys_data, series_id)
		if self.censys_api_response_has_error(series):
			self.cc_log("WARNING", "Failed to get the series for %s - error(%s)" % (series_id, series["error_code"]))
			return None

		latest_dataset = series["results"]["latest"]
		latest_dataset_ts = datetime.datetime.strptime(latest_dataset["timestamp"], "%Y%m%dT%H%M%S")
		self.cc_log("INFO", "Found the latest dataset for series %s - Timestamp %s  with ID %s" % (self.series_id, latest_dataset_ts, latest_dataset["id"]))

		dataset = self.censys_api_view_result(censys_data, series_id, latest_dataset["id"])
		if self.censys_api_response_has_error(dataset):
			self.cc_log("WARNING", "Failed to get the result for '%s' and '%s' - error(%s)" % (series_id, latest_dataset["id"], dataset["error_code"]))
			return None

		dataset_wanted_file = dataset["files"][self.file_id]
		return latest_dataset["id"], dataset_wanted_file["compressed_download_path"]

	def via_api_get_by_date(self, censys_data, series_id, wanted_date):
		"""
		Get data via api by date.

		**Returns**:
			(``str``, ``str``) pair containing unique identifier and the compressed download path if found.
			``None`` if latest dataset was not found or failed.
		"""
		censys_date_string = self.convert_cc_currentdate_to_censys_datestring(wanted_date)
		series = self.censys_api_view_series(censys_data, series_id)
		if self.censys_api_response_has_error(series):
			self.cc_log("WARNING", "Failed to get the series for %s - error(%s)" % (series_id, series["error_code"]))
			return None
		
		found_dataset_id = None
		for result in series["results"]["historical"]:
			if censys_date_string+"T" in result["timestamp"]:
				found_dataset_id = result["id"]
				break

		if not found_dataset_id: 
			available_timestamps = [r["timestamp"].split("T")[0] for r in series["results"]["historical"]]
			self.cc_log("WARNING", "Did not find the timestamp for %s - available are: %s" % (censys_date_string, available_timestamps))
			return None # No dataset found for given date, return none which will stop the path in run
		
		dataset = self.censys_api_view_result(censys_data, series_id, found_dataset_id)
		if self.censys_api_response_has_error(dataset):
			self.cc_log("WARNING", "Failed to get the result for '%s' and '%s' - error(%s)" % (series_id, found_dataset_id, dataset["error_code"]))
			return None

		dataset_wanted_file = dataset["files"][self.file_id]
		return found_dataset_id, dataset_wanted_file["compressed_download_path"]

	def via_api_get_by_datasetId(self, censys_data, series_id, wanted_datasetId):
		"""
		Get data via api by direct datasetId.

		**Returns**:
			(``str``, ``str``) pair containing unique identifier and the compressed download path if found. 
			``None`` if latest dataset was not found or failed.
		"""
		dataset = self.censys_api_view_result(censys_data, series_id, wanted_datasetId)
		if self.censys_api_response_has_error(dataset):
			self.cc_log("WARNING", "Failed to get the result for '%s' and '%s' - error(%s)" % (series_id, wanted_datasetId, dataset["error_code"]))
			return None

		dataset_wanted_file = dataset["files"][self.file_id]
		return wanted_datasetId, dataset_wanted_file["compressed_download_path"]

	def censys_api_response_has_error(self, response):
		"""
		Check the censys api response if it reports error (data not found, ...).

		**Returns**:
			``True`` containing an error. ``False`` if normal response without error.
		"""
		return "error_code" in response

	def censys_api_view_series(self, censys_data, series_id):
		"""
		Call the view_series method on the api.

		**Parameters**:
			censys_data : object
				The initialized censys data api module.
			series_id : str
				The wanted series_id as a str.

		**Returns**:
			Censys API response.
		"""
		return censys_data.view_series(series_id)

	def censys_api_view_result(self, censys_data, series_id, dataset_id):
		"""
		Call the view_results method on the api.

		**Parameters**:
			censys_data : object
				The initialized censys data api module.
			series_id : str
				The wanted series_id as a str.
			dataset_id : str
				The wanted dataset_id as a str.

		**Returns**:
			Censys API response.
		"""
		return censys_data.view_result(series_id, dataset_id)

	def download_file(self, url, target, chunk_size):
		"""
		Downloads a file from a url to its given target.

		**Parameters**:
			url : str
				path to the source where to download from.
			target : str
				path to the target file.
			chunk_size : int
				downloading chunk size.
		"""
		r = requests.get(url, stream=True)
		handle = open(target+".tmp", "wb")
		total_size = int(r.headers.get('content-length', 0))
		total_blocks = math.ceil(total_size//chunk_size)
		total_blocks_100 = math.ceil(total_blocks//100)

		self.cc_log("INFO", "Started download for %s with a total size of %s [0%%/100%%]" % (url, total_size))

		dl_counter = block_counter = 0
		for chunk in r.iter_content(chunk_size=chunk_size):
			handle.write(chunk)
			dl_counter += 1;
			if dl_counter >= total_blocks_100:
				block_counter += 1
				dl_counter = 0
				self.cc_log("INFO", "Downloaded (%s) - [%s%%/100%%]" % (url, block_counter))
		handle.close()
		os.rename(target+".tmp", target)

	def decompress_lz4(self, source, target, chunk_size):
		"""
		Decompresses a file from .LZ4 to its source file.

		**Parameters**:
			source : str
				path to the source file.
			target : str
				path to the target file.
			chunk_size : int
				decompress chunk size.
		"""
		compressed_filesize = os.stat(source).st_size
		total_blocks = math.ceil(compressed_filesize//chunk_size)
		total_blocks_100 = math.ceil(total_blocks//100)

		self.cc_log("INFO", "Started decompressing %s to %s with a total size of %s [0%%/100%%]" % (source, target, compressed_filesize))

		dec_counter = block_counter = 0

		d_context = lz4.frame.create_decompression_context()
		with open(source, 'rb') as f:
			with open(target+".tmp", 'wb') as d:
				while True:
					chunk = f.read(chunk_size)
					d2, b, eof = lz4.frame.decompress_chunk(d_context, chunk)
					d.write(d2)
					dec_counter += 1;
					if dec_counter >= total_blocks_100:
						block_counter += 1
						dec_counter = 0
						self.cc_log("INFO", "Decompressed (%s) - [%s%%/100%%]" % (source, block_counter))
					if eof: break
		os.rename(target+".tmp", target)

	def censys_id_is_newer(self, id1, id2):
		"""
		Compares two censys ids if id1 > id2 (id1 newer than id2)
		ID example: 20180714T1408

		**Parameters**:
			id1 : str
				First censys ID string to compare.
			id2 : str
				Second censys ID string to compare.

		**Returns**:
			``True`` if id1 newer than id2.
			``False`` if id2 newer than id1.
		"""
		censys_id_parser = "%Y%m%dT%H%M"
		datetime1 = datetime.datetime.strptime(id1, censys_id_parser)
		datetime2 = datetime.datetime.strptime(id2, censys_id_parser)
		return datetime1 > datetime2

	def parse_cc_currentdate_to_date(self, cc_date):
		"""
		Parse the CyberCaptain Placeholder Currentdate (%d%m%Y) to Datetime Date

		**Parameters**:
			cc_date : str
				the cybercaptain date string to parse to datetime date.
		**Returns**:
        	datetime date parsed from the given string.
		"""		
		return datetime.datetime.strptime(cc_date, "%d%m%Y")

	def convert_cc_currentdate_to_censys_datestring(self, cc_date):
		"""
		Parse the CyberCaptain Placeholder Currentdate (%d%m%Y) to Censys Date String (%Y%m%d)

		**Parameters**:
			cc_date : str
				the cybercaptain date string to parse and convert to censys datestring.
		**Returns**:
        	datetime as a string in the new censys format from the given string.
		"""		
		return datetime.datetime.strptime(cc_date, "%d%m%Y").strftime("%Y%m%d")

	def validate(self, kwargs):
		"""
		Validates all arguments for the censys module.

		**Parameters**:
			kwargs : dict
				contains a dictionary of all attributes.
		"""
		super().validate(kwargs)
		self.cc_log("INFO", "Data Store Censys: started validation")

		# We want to get data via api, need to have api keys and wanted version
		if not kwargs.get("apiSecret"): raise ValidationError(self, ["apiSecret"], "Parameter cannot be empty!")
		if not kwargs.get("apiId"): raise ValidationError(self, ["apiId"], "Parameter cannot be empty")
		if not kwargs.get("seriesId"): raise ValidationError(self, ["seriesId"], "Parameter cannot be empty!")
		if not kwargs.get("fileId"): raise ValidationError(self, ["fileId"], "Parameter cannot be empty - define which file needs to be obtained!")

		if kwargs.get("getByLatest") and str2bool(kwargs.get("getByLatest")):
			pass
		elif kwargs.get("getByDate"):
			if not re.match('^\d{8}$', kwargs.get("getByDate")) or not isinstance(kwargs.get("getByDate"), str): 
				raise ValidationError(self, ["getByDate"], "Check if getByDate is a string and correct format (valid ex.: '10042018')")
			try:
				self.parse_cc_currentdate_to_date(kwargs.get("getByDate"))
			except ValueError:
				raise ValidationError(self, ["getByDate"], "Was not able to parse getByDate has to e formated like '%d%m%Y'")
		elif kwargs.get("getByDatasetId"):
			if not re.match('^\d{8}T\d{4}$', kwargs.get("getByDatasetId")): 
				raise ValidationError(self, ["getByDatasetId"], "Parameter getByDatasetId has to e formated like '20180410T1408'")
		else:
			raise ValidationError(self, ["getByLatest","getByDate","getByDatasetId"], "Please define one method how to get the data!")

		if kwargs.get("getMissingDatasets") and kwargs.get("getAllMissingDatasets"): raise ValidationError(self, ["getMissingDatasets", "getAllMissingDatasets"], "Please only use one!")

		if kwargs.get("chunkSizeDownload"):
			try:
				kwargs["chunkSizeDownload"] = int(kwargs.get("chunkSizeDownload"))
			except ValueError:
				raise ValidationError(self, ["chunkSizeDownload"], "Chunk size download needs to be an integer!")

		if kwargs.get("chunkSizeDecomp"):
			try:
				kwargs["chunkSizeDecomp"] = int(kwargs.get("chunkSizeDecomp"))
			except ValueError:
				raise ValidationError(self, ["chunkSizeDecomp"], "Chunk size decompression needs to be an integer!")	
		

		self.cc_log("INFO", "Data Store Censys: finished validation")

	def inject_additional_tasks(self):
		"""
		Overwrite base method 'inject_additional_tasks'.

		Checks for additional and not yet processed results from the last run if 'getMissingDatasets' = True .
		Checks for additional and not yet processed results from the first dataset the API offers if 'getAllMissingDatasets' = True .
		
		Attention: The basic censys account will not be able to do these calls - researcher or commercial API account needed!

		**Returns**:
			``list`` with additional tasks. List contains dict {}
				-> Dict with "attributes" containing the modules adapted kwargs and "identifier" containing a specific identifier for the new task.
			``False`` if no additional tasks need to be injected.
		"""
		if self.get_missing_sets or self.get_all_missing_sets:
			mode = "GET ALL MISSING DATASETS" if self.get_all_missing_sets else "GET MISSING DATASETS BETWEEN LAST RUN AND NEWEST"
			self.cc_log("INFO", "Data Store Censys: Looking for missing datasets for series %s with mode [%s]" % (self.series_id, mode))

			c = censys.data.CensysData(api_id=self.api_id, api_secret=self.api_secret)
			series = self.censys_api_view_series(c, self.series_id)
			
			if self.censys_api_response_has_error(series):
				self.cc_log("WARNING", "Failed to get the series for %s - error(%s)" % (self.series_id, series["error_code"]))
				return False

			newest_processed_id = self.kv_store.get("newest_processed_id", section=self.moduleName)
			processed_ids = self.kv_store.get("processed_ids", section=self.moduleName)
			if not processed_ids: processed_ids = []

			additional_tasks = []
			for result in series["results"]["historical"]:
				# If option all missing datasets is set, check if ID does not exist in the processed_id list and then append
				# If option just to get missing sets from last run to the current is set, check if we have a last run and if the ID is newer than the last run and then append
				if (self.get_all_missing_sets and result["id"] not in processed_ids) or \
					(self.get_missing_sets and newest_processed_id and self.censys_id_is_newer(result["id"], newest_processed_id)):

					changed_kwargs = self.kwargs.copy()
					changed_kwargs.pop("getMissingDatasets", None) 		# Make sure missing datasets not called again on new task
					changed_kwargs.pop("getAllMissingDatasets", None)
					changed_kwargs.pop("getByLatest", None) 			# Remove get by latest as we get additional data direct via id
					changed_kwargs.pop("getByDate", None)
					changed_kwargs["getByDatasetId"] = result["id"] 	# Define id for the missing dataset
					changed_kwargs["target"] = append_str_to_filename(self.target, result["id"])

					additional_tasks.append({"attributes": changed_kwargs, "identifier": result["id"]})

			self.cc_log("DEBUG", "Total found datasets: %d" % len(series["results"]["historical"]))
			self.cc_log("DEBUG", "Additional not processed datasets: %d" % len(additional_tasks))
			
			# If the first element in additional tasks has a newer timestamp than the last -> Reverse the list so it gets processed from old to new			
			if len(additional_tasks) >= 2:
				if self.censys_id_is_newer(additional_tasks[0]["identifier"], additional_tasks[-1]["identifier"]):
					additional_tasks = list(reversed(additional_tasks))
			
			return additional_tasks

		return False

