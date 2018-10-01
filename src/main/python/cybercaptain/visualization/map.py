"""
This module contains the visualization map class.
"""
import os
import pandas as gpf
import geopandas as gpd
import matplotlib.pyplot as plt
import iso3166
from cybercaptain.utils.helpers import str2bool
from cybercaptain.utils.jsonFileHandler import json_file_reader
from cybercaptain.utils.exceptions import ValidationError, ConfigurationError
from cybercaptain.visualization.base import visualization_base

EUROPE_GEOJSON  =   os.path.join(os.path.dirname(__file__), "assets/europe.geojson")
WORLD_GEOJSON   =   os.path.join(os.path.dirname(__file__), "assets/world.geojson")

class visualization_map(visualization_base):
    """
    This class handles the map graph plotting.
    Important: Make sure to have enough memory to run plot the maps. Otherwise interpreting the map files might run almost forever.

    **Implemented type(s)**:
        heatmap:
            Display a heatmap over a selected map according to ISO 3166-1 alpha-3 or ISO 3166-1 alpha-2 country codes with
            a given value. 

	**Parameters**:
		kwargs:
			contains a dictionary of all attributes.

    **Attributes**:
        map: str
            the selected geojson map. Currently provided: 'europe'/'world'.
        type: str
            the map plot type. Currently supported: 'heatmap'.
        countryCodeAttribute: str
            the json attribute name where the country code can be found (E.g. 'location.code' will look in the given src and json line for the nested ["location"]["code"]).
        groupedValueAttribute: str
            the json attribute name where the grouped value (int) can be found (E.g. 'vulns.count' will look in the given src and json line for the nested ["vulns"]["count"]).
        colormap: str
            the selected matplotlib colormap name (https://matplotlib.org/examples/color/colormaps_reference.html).
        displayLegend: bool
            enable to display the colorbased legend on the plot.
        displayLabels: bool
            enable to display the labels on countries, to limit them use the argument 'labelsThreshold'.
        labelsThreshold: int
            configure the grouped value threshold to show the label.
        title: str
            configure the title to show.
        
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        self.alpha2_country_codes = iso3166.countries_by_alpha2

        # If subclass needs special variables define here
        self.selected_map = kwargs.get("map") # Currently supported: 'europe', 'world'
        self.geojson_map = self.get_geojson_for_attribute(kwargs.get("map"))
        self.type = kwargs.get("type")

        # Type: Heatmap
        self.country_code_attribute = kwargs.get("countryCodeAttribute")
        self.grouped_value_attribute = kwargs.get("groupedValueAttribute")
        self.colormap = kwargs.get("colormap")

        self.display_legend = str2bool(kwargs.get("displayLegend"))
        self.display_labels = str2bool(kwargs.get("displayLabels"))
        self.labels_threshold = kwargs.get("labelsThreshold")
        self.title = kwargs.get("title")


    def run(self):
        """
        The run method plots the selected map chart type.

        **Returns**:
            ``True`` if the run was successful.
            ``False`` if the run was not successful.
        """
        self.cc_log("INFO", "Data Visualization Map: Started")

        try:
            if self.type == "heatmap":
                return self.plot_heatmap()
            else:
                self.cc_log("ERROR", "An unknown map plot type was given (%s)!" % type)
                return False
        except Exception as e:
            self.cc_log("ERROR", "Failed to run map visu module (%s)!" % e)
            self.cc_log("INFO", "Data Visualization Map: Finished Run With Error")
            return False

        return False

    def plot_heatmap(self):
        """
        Plot a heatmap with the given defined country and grouped value attribute.

        **Parameters**:
            attribute : str
                Keyname for the wanted geojson map.
        **Returns**:
            ``True`` if the target with the plot was successfully written.
            ``False`` if the plot was not written to the target and it failed.
        """
        plt.rcParams['figure.figsize'] = (20, 10)

        self.cc_log("DEBUG", "Trying to read %s gejson file" % self.geojson_map)
        gp_map = gpd.read_file(self.geojson_map)

        gp_map['grouped_value'] = 0 # Init all shapes on the map with a grouped_value of 0
        gp_map['centroid'] = gp_map['geometry'].centroid # Set the center value on all shapes for labels

        # Loop through source file and read the given country code & grouped value attributes and set them on the map
        self.cc_log("DEBUG", "Trying to read %s src file" % self.src)
        json_fr = json_file_reader(self.src)

        self.cc_log("DEBUG", "Creating the heatmap...")
        while not json_fr.isEOF():
            data = json_fr.readRecord()

            country_code = data
            for a in self.country_code_attribute.split('.'):
                country_code = country_code[a]

            grouped_value = data
            for a in self.grouped_value_attribute.split('.'):
                grouped_value = grouped_value[a]

            # Geopandas method to set the grouped value to where the given country code matches
            
            # Check country code if ISO_A2 or ISO_A3 or undefined (-99) or something else
            country_code = str(country_code)
            if country_code == "-99" or country_code == "null" or country_code == "None":
                self.cc_log("WARNING", "There is an undefined country code, we skip this dataset - Please recheck to have an accurate plot!")
                continue

            if len(country_code) > 3 or len(country_code) < 2:
                self.cc_log("ERROR", "The given country code (%s) has a length of %s which is not a valid iso3166_A3 or iso3166_A2 code - Please recheck!" % (country_code, len(country_code)))
                return False

            if len(country_code) == 2:
                # ISO_A2 Code - Try to convert
                country_code_old = country_code
                if country_code not in self.alpha2_country_codes:
                    self.cc_log("WARNING", "There given iso3166 alpha2 code (%s) does not match any alpha3 code, we skip this dataset - Please recheck to have an accurate plot!" % (country_code))
                    continue

                country_code = self.alpha2_country_codes[country_code].alpha3
                self.cc_log("DEBUG", "Converted alpha2 country code '%s' to alpha3 code '%s'" % (country_code_old, country_code))

            gp_map.loc[gp_map['ISO_A3'] == country_code, 'grouped_value'] = int(grouped_value)

        json_fr.close()

        # Plot the map
        fig, ax = plt.subplots(1)
        gp_map.plot(ax=ax, column='grouped_value', cmap=self.colormap, edgecolor='black', linewidth=0.2, legend=self.display_legend)

        self.cc_log("DEBUG", "Heatmap created!")

        # Display labels if configured
        if self.display_labels: 
            props = dict(boxstyle='round', facecolor='linen', alpha=0.7)

            threshold = 0
            if self.labels_threshold: threshold = int(self.labels_threshold)
            for point in gp_map.iterrows():
                if point[1]['grouped_value'] > threshold: # Check threshold if configured
                    ax.text(point[1]['centroid'].x,point[1]['centroid'].y,point[1]['grouped_value'],horizontalalignment='center',fontsize=7,bbox=props)
            ax.axis('off')

        if self.title:
            plt.title(self.title)

        # Save the plot to the given target
        fig.savefig(self.target, bbox_inches='tight')
        plt.close('all')

        self.cc_log("INFO", 'Data Visualization Map: Finished Run Heatmap Success')
        return True

    def get_geojson_for_attribute(self, attribute):
        """
        Get the source for the geojson file according to the map location attribute.
        Currently supported: 'world', 'europe'

        **Parameters**:
            attribute : str
                Keyname for the wanted geojson map.
        **Returns**:
            ``str`` containing the file path str if the geojson file is defined for the given keyname.
            ``ConfigurationError`` if no gejson for the given keyname is defined.
        """
        if attribute == "world":
            return WORLD_GEOJSON
        if attribute == "europe":
            return EUROPE_GEOJSON
        raise ConfigurationError("No existing geojson for the give attribute %s" % attribute)

    def validate(self, kwargs):
        """
        The validate method checks if all the input arguments are correct.

        **Parameters**:
            kwargs : dict
                Contains a dict of all the arguments for the map chart visualisation.
        """
        super().validate(kwargs)
        self.cc_log("INFO", "Data Visualization Map: started validation")

        if not kwargs.get("map"): raise ValidationError(self, ["map"], "Parameter cannot be empty!")
        try:
            self.get_geojson_for_attribute(kwargs.get("map"))
        except:
            raise ValidationError(self, ["map"], "Parameter has to be 'europe' or 'world'!")

        if not kwargs.get("type"): raise ValidationError(self, ["type"], "Parameter cannot be empty!")

        if kwargs.get("type") == "heatmap":
            if not kwargs.get("countryCodeAttribute"): raise ValidationError(self, ["countryCodeAttribute"], "Parameter cannot be empty!")
            if not kwargs.get("groupedValueAttribute"): raise ValidationError(self, ["groupedValueAttribute"], "Parameter cannot be empty!")
            if not kwargs.get("colormap"): raise ValidationError(self, ["colormap"], "Parameter cannot be empty!")
            if kwargs.get("colormap") not in plt.colormaps(): raise ValidationError(self, ["colormap"], "Colormap has to be existing, check the matplotlibb docu!")
            if kwargs.get("labelsThreshold"):
                try:
                    int(kwargs.get("labelsThreshold"))
                except:
                    raise ValidationError(self, ["labelsThreshold"], "Parameter has to be an int!")
            
            # Optional Params
            #if not kwargs.get("displayLegend"): raise ValidationError(self, ["displayLegend"], "Parameter cannot be empty!")
            #if not kwargs.get("displayLabels"): raise ValidationError(self, ["displayLabels"], "Parameter cannot be empty!")
            #if not kwargs.get("labelsThreshold"): raise ValidationError(self, ["groupedValueAttribute"], "Parameter cannot be empty!")
            #if not kwargs.get("title"): raise ValidationError(self, ["title"], "Parameter cannot be empty!")
        self.cc_log("INFO", "Data Visualization Map: finished validation")
