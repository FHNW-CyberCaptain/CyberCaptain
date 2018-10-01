"""
The country module contains the processing_country class.
"""
from os import path
import geoip2.database
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.processing.base import processing_base
from cybercaptain.utils.jsonFileHandler import json_file_reader, json_file_writer

class processing_country(processing_base):
    """
    The country class allows to map a given IP to an ISO 3166-1 alpha-2 country code and add it to the datasets.
    Please provide a MaxMind GeoLite2-Country DB (.mmdb) yourself via the maxMindDbPath attribute.

    Important: This module will NOT work with a City, Anonymous, ASN, Connection-Type, ... MaxMind database! Only country supported!

    **Parameters**:
        kwargs :
            contains a dictionary of all attributes.

    **Script Attributes**:
        ipInputAttribute:
            a str to where the IP attribute can be found in the give source dataset.
        outputAttribute:
            a str to where (& which key) output the ISO 3166-1 alpha-2 country code.
        maxMindDbPath:
            a str to where the maxmind GeoIP database is located.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # If subclass needs special variables define here
        self.ip_input_attribute = kwargs.get("ipInputAttribute")
        self.output_attribute = kwargs.get("outputAttribute")
        self.max_mind_db_path = kwargs.get("maxMindDbPath")

    def run(self):
        """
        Runs the clean algorythm.

        **Returns**:
            ``True`` if this run succeeded.
            ``False`` if this run did not succeed.
        """
        self.cc_log("INFO", "Data Processing Country: Started")

        self.cc_log("DEBUG", "Trying to open the MaxMind GeoLite2-Country DB, please wait!")
        try:
            db = geoip2.database.Reader(self.max_mind_db_path)
        except Exception as e:
            self.logger.exception(e)
            self.cc_log("ERROR", "Failed to open the MaxMind GeoLite2-Country DB at %s - please check the file!" % (self.max_mind_db_path))
            return False
        self.cc_log("DEBUG", "Opened the MaxMindGeoLite2-Country DB!")

        json_fr = json_file_reader(self.src)
        json_fw = json_file_writer(self.target)

        self.cc_log("INFO", "Started to lookup ips and write into the target, please wait!")

        while not json_fr.isEOF():
            data = json_fr.readRecord()

            country_code = "-99"
            found_ip = data
            for attribute in self.ip_input_attribute.split('.'):
                found_ip = found_ip[attribute]

            if not found_ip or found_ip == data:
                self.cc_log("WARNING", "No IP found at the give ipInputAttribute place - Add country code -99 to this dataset!")
            else:
                # Lookup ip for country
                try:
                    ip_info = db.country(found_ip)
                    if ip_info.country.iso_code: country_code = ip_info.country.iso_code
                    self.cc_log("DEBUG", "Found country code %s for ip %s" % (ip_info.country.iso_code, found_ip))
                except Exception as e:
                    self.cc_log("WARNING", "No country code found for ip %s - add -99 to country code" % (found_ip))

            data[self.output_attribute] = country_code
            json_fw.writeRecord(data)

        json_fr.close()
        json_fw.close()
        db.close()

        self.cc_log("INFO", "Data Processing Country: Finished")
        return True

    def validate(self, kwargs):
        """
        Validates all arguments for the country module.
        kwargs(dict): contains a dictionary of all attributes.
        """
        super().validate(kwargs)
        self.cc_log("INFO", "Data Processing Country: started validation")

        if not kwargs.get("ipInputAttribute"): raise ValidationError(self, ["ipInputAttribute"], "Parameter cannot be empty!")
        if not kwargs.get("outputAttribute"): raise ValidationError(self, ["outputAttribute"] , "Parameters cannot be empty!")
        if "." in kwargs.get("outputAttribute"): raise ValidationError(self, ["outputAttribute"] , "Parameters outputAttribute can not be a nested attribute - please configure a toplevel key!")
        if not kwargs.get("maxMindDbPath"): raise ValidationError(self, ["maxMindDbPath"] , "Parameters cannot be empty!")
        if ".mmdb" not in kwargs.get("maxMindDbPath"): raise ValidationError(self, ["maxMindDbPath"] , "Please only configure MaxMind-DBs for the path (.mmdb)!")
        if not path.isfile(kwargs.get("maxMindDbPath")): raise ValidationError(self, ["maxMindDbPath"] , "Please configure an existing path to an existing MaxMind-DB!")
            
        self.cc_log("INFO", "Data Processing Country: finished validation")