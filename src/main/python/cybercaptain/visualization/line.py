"""
This module contains the visualization line class.
"""
import glob
import re
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.visualization.base import visualization_base
from cybercaptain.utils.jsonFileHandler import json_file_reader
from cybercaptain.utils.helpers import str2bool

class visualization_line(visualization_base):
    """
    This class handles the line graph plotting.

	**Parameters**:
		kwargs:
			contains a dictionary of all attributes.

    **Attributes**:
        type:
            the defined bar plot type (Currently supported: groupedlineplot, comparedlineplot)
        dataAttribute:
            in which attribute the values can be found in the dataset (E.g. 'example1.test.val')
            Recommended to use the group-module and reuse the there set value attribute here.
        groupNameAttribute:
            in which attribute the grouped name can be found (E.g. 'example1.test.group')
            Recommended to use the group-module and reuse the there set group attribute here.
        ylabel:
            the string for the y-axis.
        xlabel:
            the string for the x-axis.
        title:
            the string for the title.
        lineStyle:
            define the used linestyle (Default: solid line - Reference: https://matplotlib.org/gallery/lines_bars_and_markers/line_styles_reference.html)
        markerStyle:
            define the used markerstyle (Default: solid dot - Reference: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.plot.html)
        threshold:
            possibility to set a value threshold to hide smaller groups for example.
        figureSize:
            define a tuple to set the figure size proportion (E.g. '20, 10').
        rotateXTicks:
            int to rotate the x-ticks names if needed (E.g. 90 or -90).
        filenamesRegexExtract:
            enables to extract stuff from the filenames to for example use on the x/y axis of file/run grouped plots (E.g. '(\d)').
        colormapAscending:
            normalizes given values and set a color depending on their value (Ascending heat - possible to combine with 'colormap').
            (Supported: None) 
        colormap:
            set the string for the colormap to be used on the graphs (Reference: https://matplotlib.org/users/colormaps.html).
        showGrid:
            show the grid behind the plot (Defaults to False).
        showLegend:
            show the data legend for the chart (Defaults to True).
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # If subclass needs special variables define here
        self.type = kwargs.get("type")

        # General
        self.data_attribute = kwargs.get("dataAttribute") # In which attribute to find the group value in the dataset
        self.group_name_attribute = kwargs.get("groupNameAttribute") # In which attribute to find the group name in the dataset
        self.y_label = kwargs.get("ylabel", "")
        self.x_label = kwargs.get("xlabel", "")
        self.title = kwargs.get("title", "")
        self.line_style = kwargs.get("lineStyle", "-")
        self.marker_style = kwargs.get("markerStyle", "o")
        self.threshold = kwargs.get("threshold")
        self.figure_size = kwargs.get("figureSize", [20, 10])
        self.filenames_regex_extract = kwargs.get("filenamesRegexExtract")
        self.color_map_ascending = kwargs.get("colormapAscending")
        self.color_map = kwargs.get("colormap")
        self.rotate_xticks = kwargs.get("rotateXTicks", 0)
        self.show_grid = str2bool(kwargs.get("showGrid"))
        self.show_legend = str2bool(kwargs.get("showLegend"))

    def run(self):
        """
        The run method collects and bundles the data for the line plotting method.

        **Returns**:
            ``True`` if the run was successful.
            ``False``if the run did not end successful.
        """
        self.cc_log("INFO", "Data Visualization Line: Started")
        success = False

        self.cc_log("INFO", "Line visualization type: %s" % self.type)
        plt.rcParams['figure.figsize'] = (self.figure_size[0], self.figure_size[1])
       
        files = glob.glob(self.src)

        if len(files) < 1:
            self.cc_log("ERROR", "No files to plot were found - maybe recheck wildcard if defined!")
            return False

        if self.type == "groupedlineplot":
            success = self.plot_groupedlineplot(files)
        elif self.type == "comparedlineplot":
            success = self.plot_comparedlineplot(files)
        else:
            self.cc_log("ERROR", "Data Visualization Line: An unknown line plot type (%s) was defined!" % (self.type))
            return False

        if success:
            self.cc_log("DEBUG", "Data Visualization Line: The plot can be found at: %s" % self.target)
            self.cc_log("INFO", "Data Visualization Line: Finished")
            return True

        return False

    def plot_groupedlineplot(self, files):
        """
		Plots a simple line plot where the x-axis represents the groups and the lines the different runs/files.

		**Parameters**:
			files : list
				list of file paths.

        **Returns**:
            ``True`` if the plot was successfully saved.
            ``False`` in case something failed.
		"""
        _, ax = plt.subplots()

        file_count, names_list, data_dict = self.get_data_from_files(files)

        if len(data_dict) == 0:
            self.cc_log("WARNING", "Data length to plot is equal to zero - recheck dataAttribute, groupNameAttribute or threshold!")
            return False

        data_vals = list(data_dict.values())
        data_keys = list(data_dict.keys())

        self.set_color_cycle(len(data_keys), ax)

        ticks = np.arange(len(data_keys))
        for i in range(file_count):
            plot_values = [ x[i] for x in data_vals ]
            #custom_colormap = self.get_heat_colormap(plot_values) # Ascending Heat If Activated
            plt.plot(ticks, plot_values, linestyle=self.line_style, marker=self.marker_style, label = names_list[i])

        plt.xticks(ticks, data_keys, rotation=self.rotate_xticks)
        ax.set_ylabel(self.y_label, fontweight='bold')
        ax.set_xlabel(self.x_label, fontweight='bold')
        ax.set_title(self.title, fontweight='bold')
        if self.show_legend: ax.legend(loc = 'best')
        if self.show_grid: plt.grid(linestyle='dotted')
        plt.savefig(self.target, bbox_inches='tight')
        plt.close('all')

        return True

    def plot_comparedlineplot(self, files):
        """
		Plots a simple line plot where the x-axis represents the diffeent runs / files to compare data over time.

		**Parameters**:
			files : list
				list of file paths.

        **Returns**:
            ``True`` if the plot was successfully saved.
            ``False`` in case something failed.
		"""
        _, ax = plt.subplots()

        file_count, names_list, data_dict = self.get_data_from_files(files)

        if len(data_dict) == 0:
            self.cc_log("WARNING", "Data length to plot is equal to zero - recheck dataAttribute, groupNameAttribute or threshold!")
            return False

        data_vals = list(data_dict.values())
        data_keys = list(data_dict.keys())

        self.set_color_cycle(len(data_keys), ax)

        for i in range(len(data_keys)):
            #custom_colormap = self.get_heat_colormap(data_vals[i]) # Ascending Heat If Activated
            #plt.scatter(np.arange(file_count), data_vals[i], cmap=custom_colormap, vmin=min(data_vals[i]),vmax=max(data_vals[i]) )
            plt.plot(np.arange(file_count), data_vals[i], linestyle=self.line_style, marker=self.marker_style, label = data_keys[i])

        plt.xticks(np.arange(file_count), names_list, rotation=self.rotate_xticks)
       
        ax.set_ylabel(self.y_label, fontweight='bold')
        ax.set_xlabel(self.x_label, fontweight='bold')
        ax.set_title(self.title, fontweight='bold')
        if self.show_legend: ax.legend(loc = 'best')
        if self.show_grid: plt.grid(linestyle='dotted')
        plt.savefig(self.target, bbox_inches='tight')
        plt.close('all')

        return True

    def set_color_cycle(self, amount, ax, colormap_name="tab20"):
        """
		Sets the color cycle for the plot according to the amount needed.

		**Parameters**:
			amount : int
				amount of colors needed.
            ax : MatplotLib Axes Object
                the axes subplot object to set the colors on.
            colormap_name : MatplotLib ColorMap
                the wanted colormap to set (More infos on: https://matplotlib.org/users/colormaps.html)
                Default 'tab20'
		"""
        if self.color_map: colormap_name = self.color_map
        cmap = plt.get_cmap(colormap_name)
        ax.set_prop_cycle(plt.cycler('color', cmap(np.linspace(0, 1, amount))))

    def get_heat_colormap(self, values, colormap="Reds"):
        """
		Returns a custom heat asscending colormap according to the given values.

		**Parameters**:
			values : list
				list of the values to normalize and get the heat ascending matplotlib colormap back.
            colormap : str
                possibility to use a custom heat ascending colormap (Default: Reds)

        **Returns**:
            ``list`` containing a matplotlib color depending on the previous given value.
            ``None`` if 'colormapAscending' is not configured or False
		"""
        if self.color_map: colormap = self.color_map
        if not self.color_map_ascending: return None
        cNorm  = colors.Normalize(vmin=min(values), vmax=max(values))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=plt.get_cmap(colormap))
        return [scalarMap.to_rgba(v) for v in values] 

    def get_data_from_files(self, files):
        """
		Gets and extracts the data from the given fileslist.

		**Parameters**:
			files : list
				list of filepaths to process.

        **Returns**:
            ``file_count, names_list, data_dict`` amount of files, names list of the files, grouped data dict with the values scaled in case of missing data
		"""
        data_dict = {}
        names_list = []
        file_count = 0

        for file in files:
            json_fr = json_file_reader(file)
            while not json_fr.isEOF():
                json_data = json_fr.readRecord()

                value = json_data
                for a in self.data_attribute.split('.'):
                    value = value[a]

                # Threshold
                if self.threshold and int(value) < int(self.threshold):
                    continue # Skip this line as its < threshold

                group_name = json_data
                for a in self.group_name_attribute.split('.'):
                    group_name = group_name[a]

                if group_name in data_dict:
                    data_dict[group_name].append(value)
                else:
                    data_dict[group_name] = [0] * file_count
                    data_dict[group_name].append(value)

            for gn in data_dict:
                if len(data_dict[gn]) < file_count+1: # Will not be appended as filecount isnt incremented yet, +1 added
                    data_dict[gn].append(0)

            json_fr.close()

            # Add filenames list to names list or extract regex if defined
            name = None
            if self.filenames_regex_extract:
                name = re.search(self.filenames_regex_extract, os.path.basename(file))
                if name: name = name.group(0)
            if not name: name = os.path.basename(file)
            names_list.append(name)
            
            file_count += 1
        return file_count, names_list, data_dict

    def validate(self, kwargs):
        """
        The validate method checks if all the input arguments are corret.

        **Parameters**:
            kwargs : dict
                Contains a dict of all the arguments for the line chart visualisation.
        """
        super().validate(kwargs)
        self.cc_log("INFO", "Data Visualization Line: started validation")

        if not kwargs.get("type"):
            raise ValidationError(self, ["type"], "Parameter cannot be empty!")
        if not kwargs.get("dataAttribute"):
            raise ValidationError(self, ["dataAttribute"], "Parameter cannot be empty!")
        if not kwargs.get("groupNameAttribute") and kwargs.get("type") != "histogram":
            raise ValidationError(self, ["groupNameAttribute"], "Parameter cannot be empty!")
        if kwargs.get("threshold"):
            try:
                int(kwargs.get("threshold"))
            except:
                raise ValidationError(self, ["threshold"], "Parameter has to be an int!")
        if kwargs.get("figureSize"):
            if not isinstance(kwargs.get("figureSize"), list) or len(kwargs.get("figureSize")) != 2:
                raise ValidationError(self, ["figureSize"], "Parameter has to be a list of two (E.g. 20, 10)!")
        if kwargs.get("rotateXTicks"):
            try:
                int(kwargs.get("rotateXTicks"))
            except:
                raise ValidationError(self, ["rotateXTicks"], "Parameter has to be an int!")
        if kwargs.get("colormap"):
            if kwargs.get("colormap") not in plt.colormaps(): raise ValidationError(self, ["colormap"], "Colormap has to be existing, check the matplotlibb docu!")
  
        # Optional
        #if not kwargs.get("title"):
        #    raise ValidationError(self, ["title"], "Parameter cannot be empty!")
        #if not kwargs.get("ylabel"):
        #    raise ValidationError(self, ["ylabel"], "Parameter cannot be empty!")
        #if not kwargs.get("xlabel"):
        #    raise ValidationError(self, ["xlabel"], "Parameter cannot be empty!")
        #if not kwargs.get("lineStyle"):
        #    raise ValidationError(self, ["lineStyle"], "Parameter cannot be empty!")
        #if not kwargs.get("markerStyle"):
        #    raise ValidationError(self, ["markerStyle"], "Parameter cannot be empty!")
        #if not kwargs.get("filenamesRegexExtract"):
        #    raise ValidationError(self, ["filenamesRegexExtract"], "Parameter cannot be empty!")       
        #if not kwargs.get("showGrid"):
        #    raise ValidationError(self, ["showGrid"], "Parameter cannot be empty!")

        self.cc_log("INFO", "Data Visualization Line: finished validation")