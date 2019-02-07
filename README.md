<p align="center">
  <img src="https://gitlab.fhnw.ch/IP56/cybercaptain/uploads/5296e9e1031aba85ae63a2618f8755f3/Logo_CyberCaptain_1_sm.jpg" alt="CybercaptainLogo" />
</p>

# CyberCaptain
CyberCaptain has the goal of simplifing the process of analising data from different sources (e.g. censys or shodan.io). This will be achived by defining and implementing a new scripting language; which allows the programmer to define the steps needed for the desired report with a minimum of boiler plate code. The CyberCaptain scripting langauge will try to be as lazy as possible and check if a previous run has already completed the steps and reuse its results. This lazy aproach will allow an efficient analisis of data over a period of time. With these features we will make looting the databases much easier, you are welcome matey, Arrrr.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Repository Guide
This respository is set up in different folders:
* `src` - This folder contains the source code.
* `docs` - This folder contains the rst files to generate the documentation with sphinx.

### Prerequisites
You need to install the following tools before you can start developing or testing on this repository.

* [Python 3.5](https://www.python.org/) or higher
* [pip](https://pip.pypa.io/en/stable/installing/) (usually comes with python)
* git (if you don't have it, well get it)

## Recommended: One-step checkout, build & run
After you have installed the basic dependencies you can get started by running
```
sudo pip install pyb-init && pyb-init git git@github.com:FHNW-CyberCaptain/CyberCaptain.git
```
This will checkout and initialise CyberCaptain in a new folder.

Afterwards, activating the venv and building can be done with (has to be run in the checked out folder e.g. `cybercaptain`)
```
source venv/bin/activate
pyb
cd target/dist/cybercaptain-$VERSION
```

Finally CyberCaptain can be run with
```
python runCybercaptain.py -c <pathToConfigFile> [options]
```

### Run with GUI (Additional steps required)
To be able to run with a GUI, you have to make sure that you are running a Python Framework version and have [wxPython](https://wxpython.org/) & [Gooey](https://github.com/chriskiehl/Gooey) installed.
If the system is compatible and the previous steps are done, run with (attention to `pythonw`):
```
pythonw runCybercaptainGui.py
```

<p align="center">
  <img src="https://gitlab.fhnw.ch/IP56/cybercaptain/uploads/b1f87865b7ddc547caa8d9b76a1b151b/cybercaptain_gui_sm.png" alt="CybercaptainGUI" />
</p>

## Manual: Installation, tests, docs & deploy
### Installing
After you have installed the basic dependencies and checked out the repository, you can get started by running 
```
pip install pybuilder
```
in your terminal following by
```
pyb install_dependencies
```

This will install all the dependencies and run the tests. After it has finish you should see a message like this:
```
------------------------------------------------------------
BUILD SUCCESSFUL
------------------------------------------------------------
Build Summary
             Project: cybercaptain
             Version: 1.0.dev0
      Base directory: /path/to/cybercaptain
        Environments: 
               Tasks: install_dependencies [2799 ms]
Build finished at 2018-04-03 09:36:23
Build took 2 seconds (2811 ms)
```

#### Windows Speciality
The command `pyb install_dependencies` will faile cause of the geopanda dependecy. This is why geopanda has to be installed manually following the instructions of this blog [Using geopandas on Windows](https://geoffboeing.com/2014/09/using-geopandas-windows/).

## Running tests
If you want to deploy or test the project just run the 
```
pyb run_unit_tests
```
command on it's own. You will find the test results in the folder `target/reports/`.

## Running coverage
If you want to see the test coverage you can run
```
pyb analyze
```
This target depends on `pyb run_unit_tests` and therefore runs it too.

## Deployment
To deploy the project simply run 
```
pyb publish
```
This will run all the tests and generate the `target/dist` folder, which contains a `setup.py` for installing the interperter seperatly.

### Run
After exectuing the needed "Deployment" task, CyberCaptain can be run entering the folder `target/dist/cybercaptain-$VERSION` and by calling
```
python runCybercaptain.py -c <pathToConfigFile> [options]
```

## Automatic Documentation
To automatically generate the documentation from the source code we deploy the use of Sphinx. To add new modules and apis to the documentation run 
```
sphinx-apidoc -f -M --implicit-namespaces -e -o docs/ src/main/python/cybercaptain/
```

To generate the HTML code run
```
pyb sphinx_generate_documentation
```

## Built With
* [PyBuilder](http://pybuilder.github.io/) - Dependency Management
* [Sphinx](http://www.sphinx-doc.org/) - Source Documentation Generation
* [configobj](https://github.com/DiffSK/configobj) - Config File Reader
* [matplotlib](https://pypi.org/project/matplotlib/) - 2D Graphics
* [numpy](https://pypi.org/project/numpy/) - Array Processing
* [requests](https://pypi.org/project/requests/) - HTTP For Humans
* [lz4](https://pypi.org/project/numpy/) - LZ4 Bindings, Compression
* [censys](https://pypi.org/project/censys/) - censys API
* [shodan](https://pypi.org/project/shodan/) - Shodan API
* [responses](https://pypi.org/project/responses/) - Mock Requests Lib
* [BTrees](https://pypi.org/project/BTrees/) - Scalable Object Containers
* [geoip2](https://pypi.org/project/geoip2/) - MaxMind GeoIP2 API
* [pandas](https://pypi.org/project/pandas/) - Data Structure (Used for maps)
* [geopandas](https://pypi.org/project/geopandas/) - Geographic Panda Extension
* [descartes](https://pypi.org/project/descartes/) - Geo Objects
* [iso3166](https://pypi.org/project/iso3166/) - ISO 3166-1 country definitions
* [Jinja2](https://pypi.org/project/Jinja2/) - Template Engine

## Our file endings
Because the CyberCaptain writes and defines different files. To easaly differenciate we recomend to follow this convention:
* CyberCaptain Script (.ccs)
* CyberCaptain Source File (.ccsf)
* CyberCaptain Target File  (.cctf)
* CyberCaptain Cache File (.cccf)
* CyberCaptain Config File (.ccc)

# Authors
This Project is a bachelor thesis of the Fachhochschule Nordwest Schweiz (FHNW).

**Supervisor**:
* Martin Gwerder

**Students**:
* Nick Thommen
* Tobias Wilcke

## Further Reading
This project started as a Bachelor Thesis. As such a report has been written, an adjusted version of the handed in Version is published with this repository as a PDF. This report explains CyberCaptain in depth.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
