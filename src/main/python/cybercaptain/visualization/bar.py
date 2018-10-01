"""
This module contains the visualization bar class.
"""
import glob
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import FuncFormatter
from cybercaptain.utils.exceptions import ValidationError
from cybercaptain.visualization.base import visualization_base
from cybercaptain.utils.jsonFileHandler import json_file_reader
from cybercaptain.utils.helpers import str2bool

class visualization_bar(visualization_base):
    """
    This class handles the bar graph plotting.

	**Parameters**:
		kwargs:
			contains a dictionary of all attributes.

    **Attributes**:
        type:
            the defined bar plot type (Currently supported: histogram, comparedbarplot, groupedbarplot, barplot3d, barplotgroupedstacked, barplotcomparedstacked)
        dataAttribute:
            in which attribute the values can be found in the dataset (E.g. 'example1.test.val')
            Recommended to use the group-module and reuse the there set value attribute here.
        groupNameAttribute:
            in which attribute the grouped name can be found (E.g. 'example1.test.group')
            Recommended to use the group-module and reuse the there set group attribute here.
        threshold:
            possibility to set a value threshold to hide smaller groups for example.
        figureSize:
            define a tuple to set the figure size proportion (E.g. '20, 10').
        rotateXTicks:
            int to rotate the x-ticks names if needed (E.g. 90 or -90).
        rotateYTicks:
            int to rotate the y-ticks names if needed (E.g. 90 or -90).
        filenamesRegexExtract:
            enables to extract stuff from the filenames to for example use on the x/y axis of file/run grouped plots (E.g. '([-+]\\d+)').
        colormapAscending:
            normalizes given values and set a color depending on their value (Ascending heat - possible to combine with 'colormap')
            (Supported for: comparedbarplot, groupedbarplot, barplot3d  - Defaults to False)
            (Important: Ascending heat colors do not make sense for every plot although it is supported!)
        colormap:
            set the string for the colormap to be used on the graphs (Reference: https://matplotlib.org/users/colormaps.html)
        horizontal:
            the bool to display the barchart horizontal to the default vertical (Supported for: comparedbarplot, groupedbarplot, barplotcomparedstacked, barplotgroupedstacked)
        scaledTo100:
            the bool to scale a stacked bar plot to 100 (Supported for: barplotcomparedstacked, barplotgroupedstacked)
        xlabel:
            the string for the x-axis.
        ylabel:
            the string for the y-axis.
        title:
            the string for the title.
        zlabel:
            the string for the z-axis.
        showYAxisFileNames:
            the bool if on the BarPlot3D plot the filenames should be shown on the y-axis.
            Can be combined with filenamesRegexExtract to just get certain things.
        showGrid:
            show the grid behind the plot (Defaults to False).
        showLegend:
            show the data legend for the chart (Defaults to True).
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate(kwargs)

        # If subclass needs special variables define here
        self.type = kwargs.get("type") # Histogram, ComparedBarPlot, GroupedBarPlot, BarPlot3D, StackedBarPlot, GroupedBarPlot
        
        # General
        self.data_attribute = kwargs.get("dataAttribute") # In which attribute to find the group value in the dataset
        self.group_name_attribute = kwargs.get("groupNameAttribute") # In which attribute to find the group name in the dataset
        self.x_label = kwargs.get("xlabel", "")
        self.y_label = kwargs.get("ylabel", "")
        self.title = kwargs.get("title", "")
        self.threshold = kwargs.get("threshold")
        self.figure_size = kwargs.get("figureSize", [20, 10])
        self.filenames_regex_extract = kwargs.get("filenamesRegexExtract")
        self.color_map_ascending = str2bool(kwargs.get("colormapAscending"))
        self.color_map = kwargs.get("colormap")
        self.rotate_xticks = kwargs.get("rotateXTicks", 0)
        self.rotate_yticks = kwargs.get("rotateYTicks", 0)
        self.horizontal = str2bool(kwargs.get("horizontal"))
        self.show_grid = str2bool(kwargs.get("showGrid"))
        self.show_legend = str2bool(kwargs.get("showLegend", True))

        # Stacked Plots
        self.scaled_to_100 = str2bool(kwargs.get("scaledTo100"))

        # BarPlot3D
        self.z_label = kwargs.get("zlabel", "")
        self.show_y_axis_file_names = str2bool(kwargs.get("showYAxisFileNames"))


    def run(self):
        """
        The bar run method collects and bundles the data for the plotting method.

        **Returns**:
            ``True`` if the run was successful.
            ``False``if the run did not end successful.
        """
        self.cc_log("INFO", "Data Visualization Bar: Started")
        success = False

        self.cc_log("INFO", "Bar visualization type: %s" % self.type)
        plt.rcParams['figure.figsize'] = (self.figure_size[0], self.figure_size[1])

        files = glob.glob(self.src)

        if len(files) < 1:
            self.cc_log("ERROR", "No files to plot were found - maybe recheck wildcard if defined!")
            return False

        if self.type == "histogram":
            success = self.plot_histogram(files)
        elif self.type == "comparedbarplot":
            success = self.plot_comparedbarplot(files)
        elif self.type == "groupedbarplot":
            success = self.plot_groupedbarplot(files)
        elif self.type == "barplot3d":
            success = self.plot_barplot3d(files)
        elif self.type == "barplotcomparedstacked":
            success = self.plot_barplotcomparedstacked(files)
        elif self.type == "barplotgroupedstacked":
            success = self.plot_barplotgroupedstacked(files)
        else:
            self.cc_log("ERROR", "Data Visualization Bar: An unknown bar plot type (%s) was defined!" % (self.type))
            return False
        
        if success:
            self.cc_log("DEBUG", "Data Visualization Bar: The plot can be found at: %s" % self.target)
            self.cc_log("INFO", "Data Visualization Bar: Finished")
            return True

        return False

    def plot_comparedbarplot(self, files):
        """
		Plots a simple compared barplot according to the groups and their values.
        Multiple files/runs will show on the X-Axis and different groups beside eachother.

        (colormapAscending supported - ascending heat for every group)

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

        barWidth = 1/len(data_keys)
        x_pos = np.arange(file_count)

        for i in range(0, len(data_keys)):
            custom_colormap = self.get_heat_colormap(data_vals[i]) # Ascending Heat If Activated

            if self.horizontal:
                plt.barh(x_pos, data_vals[i], height=barWidth, color=custom_colormap, edgecolor='white', label=data_keys[i])
                x_pos = [p + barWidth for p in x_pos]
            else:
                plt.bar(x_pos, data_vals[i], width=barWidth, color=custom_colormap, edgecolor='white', label=data_keys[i])
                x_pos = [p + barWidth for p in x_pos]      
        
        #data_keys_expanded = data_keys*file_count
        #data_keys_expanded[0] = data_keys_expanded[0] + "\n"+names_list[0]
        #for i in range(1, file_count):
        #    data_keys_expanded[i*len(data_keys)] = data_keys_expanded[i*len(data_keys)] + "\n"+names_list[i]

        plt.xticks([0], names_list, rotation=self.rotate_xticks)
        if self.horizontal:
            plt.yticks(np.arange(file_count), names_list, rotation=self.rotate_yticks)
        else:
            plt.xticks(np.arange(file_count), names_list, rotation=self.rotate_xticks)

        ax.set_ylabel(self.y_label, fontweight='bold')
        ax.set_xlabel(self.x_label, fontweight='bold')
        ax.set_title(self.title, fontweight='bold')
        if self.show_legend: ax.legend(data_keys, loc = 'best')
        if self.show_grid: plt.grid(linestyle='dotted')
        plt.savefig(self.target, bbox_inches='tight')
        plt.close('all')

        return True

    def plot_groupedbarplot(self, files):
        """
		Plots a simple grouped barplot according to the groups and their values.
        Multiple files/runs will show beside each other. X-Axis resembles the groups.

        (colormapAscending supported - ascending heat colors for every run/file)

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

        barWidth = 1/file_count
        x_pos = np.arange(len(data_vals))

        for i in range(0, file_count):
            plot_values = [ x[i] for x in data_vals ]
            custom_colormap = self.get_heat_colormap(plot_values) # Ascending Heat If Activated
            
            if self.horizontal:
                plt.barh(x_pos, plot_values, height=barWidth, color=custom_colormap, edgecolor='white', label=names_list[i])
                x_pos = [x + barWidth for x in x_pos]
            else:
                plt.bar(x_pos, plot_values, width=barWidth, color=custom_colormap, edgecolor='white', label=names_list[i])
                x_pos = [x + barWidth for x in x_pos]

        if self.horizontal:
            plt.yticks(np.arange(len(data_vals)), data_keys, rotation=self.rotate_yticks)
        else:
            plt.xticks(np.arange(len(data_vals)), data_keys, rotation=self.rotate_xticks)

        ax.set_ylabel(self.y_label, fontweight='bold')
        ax.set_xlabel(self.x_label, fontweight='bold')
        ax.set_title(self.title, fontweight='bold')
        if self.show_legend: ax.legend(loc = 'best')
        if self.show_grid: plt.grid(linestyle='dotted')
        plt.savefig(self.target, bbox_inches='tight')
        plt.close('all')

        return True

    def plot_barplot3d(self, files):
        """
		Plots a barplot plot in 3D x axis according to the groups.
        Multiple files/runs will show on the z axis.

        (colormapAscending supported - ascending heat colors for every run/file)

		**Parameters**:
			files : list
				list of file paths.

        **Returns**:
            ``True`` if the plot was successfully saved.
            ``False`` in case something failed.
		"""
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        file_count, names_list, data_dict = self.get_data_from_files(files)

        if len(data_dict) == 0:
            self.cc_log("WARNING", "Data length to plot is equal to zero - recheck dataAttribute, groupNameAttribute or threshold!")
            return False

        data_vals = list(data_dict.values())
        data_keys = list(data_dict.keys())
        self.set_color_cycle(len(data_keys), ax)

        for i in range(0, file_count):
            plot_values = [ x[i] for x in data_vals ]
            custom_colormap = self.get_heat_colormap(plot_values) # Ascending Heat If Activated

            ax.bar(np.arange(len(data_keys)), plot_values, color=custom_colormap, zs=i, zdir='y', alpha=0.8)

        ax.set_xticks(np.arange(len(data_keys)))
        ax.set_xticklabels(data_keys, rotation=self.rotate_xticks)

        ax.set_yticks(np.arange(file_count))
        
        if self.show_y_axis_file_names:
            ax.set_yticklabels(names_list, ha="left")
        else:
            ax.set_yticklabels([])

        ax.set_xlabel(self.x_label, y=1.10, labelpad=20, fontweight='bold')
        ax.set_ylabel(self.y_label, fontweight='bold')
        ax.set_zlabel(self.z_label, fontweight='bold')
        ax.set_title(self.title, y=1.02, fontweight='bold')
        if self.show_grid: plt.grid(linestyle='dotted')
        plt.savefig(self.target, bbox_inches='tight')
        plt.close('all')

        return True

    def plot_barplotgroupedstacked(self, files):
        """
		Plots a simple barplot according to the groups and their values.
        Multiple files/runs will be shown stacked on each of the groups.

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
        barWidth = 0.9

        bottom = np.array([0] * len(data_keys))
        if self.scaled_to_100: totals = [sum(x) for x in data_vals]

        for i in range(0, file_count):
            plot_values = [ x[i] for x in data_vals ]

            if self.scaled_to_100: plot_values = [l / j * 100 for l,j in zip(plot_values, totals)]
            
            if self.horizontal:
                ax.barh(np.arange(len(data_keys)), plot_values, linewidth=0, height=barWidth, left=bottom, label=names_list[i])
                bottom = bottom + plot_values
            else:
                ax.bar(np.arange(len(data_keys)), plot_values, linewidth=0, width=barWidth, bottom=bottom, label=names_list[i])
                bottom = bottom + plot_values

        if self.horizontal:
            ax.set_yticks(np.arange(len(data_keys)))
            ax.set_yticklabels(data_keys, rotation=self.rotate_yticks)
            if self.scaled_to_100: ax.xaxis.set_major_formatter(FuncFormatter(lambda y, pos: "%d%%" % (y)))
        else:
            ax.set_xticks(np.arange(len(data_keys)))
            ax.set_xticklabels(data_keys, rotation=self.rotate_xticks)
            if self.scaled_to_100: ax.yaxis.set_major_formatter(FuncFormatter(lambda y, pos: "%d%%" % (y)))

        ax.set_ylabel(self.y_label, fontweight='bold')
        ax.set_xlabel(self.x_label, fontweight='bold')
        ax.set_title(self.title, fontweight='bold')
        if self.show_legend: ax.legend(loc = 'best')
        if self.show_grid: plt.grid(linestyle='dotted')
        plt.savefig(self.target, bbox_inches='tight')
        plt.close('all')

        return True

    def plot_barplotcomparedstacked(self, files):
        """
		Plots a simple barplot but with the different files/runs shown on the x_axis.
        Different groups/values are stacked.


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

        data_to_plot_length = len(data_vals[0])

        self.set_color_cycle(len(data_keys), ax)
        
        
        ind = np.arange(data_to_plot_length)    # the x locations for the groups
        width = 0.9         # the width of the bars: can also be len(x) sequence
        bottom = [0] * data_to_plot_length      # init a list with zeros for bottom
        
        plts = [] 

        if self.scaled_to_100: totals = [sum(x) for x in zip(*data_vals)]
       
        for single_data_set in data_vals:
            if self.scaled_to_100: single_data_set = [i / j * 100 for i,j in zip(single_data_set, totals)]

            if self.horizontal:
                plts.append(plt.barh(ind, single_data_set, linewidth=0, height=width, left=bottom))
            else:
                plts.append(plt.bar(ind, single_data_set, linewidth=0, width=width, bottom=bottom))      

            for i in range(len(single_data_set)):
                bottom[i] = bottom[i] + single_data_set[i]

        if self.horizontal:
            plt.yticks(ind, names_list, rotation=self.rotate_yticks)
            if self.scaled_to_100: ax.xaxis.set_major_formatter(FuncFormatter(lambda y, pos: "%d%%" % (y)))
        else:
            plt.xticks(ind, names_list, rotation=self.rotate_xticks)
            if self.scaled_to_100: ax.yaxis.set_major_formatter(FuncFormatter(lambda y, pos: "%d%%" % (y)))

        plt.ylabel(self.y_label, fontweight='bold')
        plt.xlabel(self.x_label, fontweight='bold')
        plt.title(self.title, fontweight='bold')
        if self.show_legend: plt.legend(plts, data_keys, loc='best', bbox_to_anchor=(1, 0.5))
        plt.subplots_adjust(right=0.7)
        if self.show_grid: plt.grid(linestyle='dotted')
        plt.savefig(self.target, bbox_inches='tight')
        plt.close('all')
        
        return True

    def plot_histogram(self, files):
        """
		Plots a histogram.

		**Parameters**:
			files : list
				list of file paths.

        **Returns**:
            ``True`` if the plot was successfully saved.
            ``False`` in case something failed.
		"""
        _, ax = plt.subplots()
        values_list = []
        names_list = []
        for file in files:
            json_fr = json_file_reader(file)

            values = []
            while not json_fr.isEOF():
                data = json_fr.readRecord()

                value = data
                for a in self.data_attribute.split('.'):
                    value = value[a]

                # Threshold
                if self.threshold and int(value) < int(self.threshold):
                    continue # Skip this line as its < threshold
                
                values.append(value)

            json_fr.close()
            values_list.append(values)
            names_list.append(os.path.basename(file))

        self.set_color_cycle(len(names_list), ax)
        ax.hist(values_list, label = names_list, bins=10, edgecolor='white')
        ax.set_ylabel(self.y_label, fontweight='bold')
        ax.set_xlabel(self.x_label, fontweight='bold')
        ax.set_title(self.title, fontweight='bold')
        if self.show_legend: ax.legend(loc = 'best')
        if self.show_grid: plt.grid(linestyle='dotted')
        plt.savefig(self.target, bbox_inches='tight')
        plt.close('all')
        
        return True

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

    def validate(self, kwargs):
        """
        The validate method checks if all the input arguments are corret.

        **Parameters**:
            kwargs : dict
                Contains a dict of all the arguments for the line chart visualisation.
        """
        super().validate(kwargs)
        self.cc_log("INFO", "Data Visualization Bar: started validation")

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
        if kwargs.get("rotateYTicks"):
            try:
                int(kwargs.get("rotateYTicks"))
            except:
                raise ValidationError(self, ["rotateYTicks"], "Parameter has to be an int!")
        if kwargs.get("colormap"):
            if kwargs.get("colormap") not in plt.colormaps(): raise ValidationError(self, ["colormap"], "Colormap has to be existing, check the matplotlibb docu!")

        # Optional
        #if not kwargs.get("title"):
        #    raise ValidationError(self, ["title"], "Parameter cannot be empty!")
        #if not kwargs.get("ylabel"):
        #    raise ValidationError(self, ["ylabel"], "Parameter cannot be empty!")
        #if not kwargs.get("xlabel"):
        #    raise ValidationError(self, ["xlabel"], "Parameter cannot be empty!")
        #if not kwargs.get("zlabel"):
        #    raise ValidationError(self, ["zlabel"], "Parameter cannot be empty!")
        #if not kwargs.get("horizontal"):
        #    raise ValidationError(self, ["horizontal"], "Parameter cannot be empty!")
        #if not kwargs.get("scaledTo100"):
        #    raise ValidationError(self, ["scaledTo100"], "Parameter cannot be empty!")
        self.cc_log("INFO", "Data Visualization Bar: finished validation")