from pybuilder.core import init, use_plugin, Author
import logging

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("python.install_dependencies")
use_plugin("python.sphinx")

default_task = "publish"

name = "cybercaptain"
version = "1.0.0"
summary = "Simplifing the process of analising data from different sources over time."
authors = (Author("Tobias Wilcke", "tobias.wilcke@students.fhnw.ch"),
           Author("Nick Thommen", "nick.thommen@students.fhnw.ch"))
license = "MIT"

@init
def initialize(project):
    # plugin properties
    project.set_property("coverage_break_build", False)
    project.set_property("sphinx_output_dir", "target/doc/")
    # dependencies
    project.build_depends_on('configobj')
    project.build_depends_on('matplotlib')
    project.build_depends_on('numpy')
    project.build_depends_on('requests')
    project.build_depends_on('lz4')
    project.build_depends_on('censys')
    project.build_depends_on('shodan')
    project.build_depends_on('responses') # Unittests mocking
    project.build_depends_on('BTrees')
    project.build_depends_on('geoip2') # Country module - Apache License 2.0
    project.build_depends_on('pandas') # Used for map plotting
    project.build_depends_on('geopandas')
    project.build_depends_on('descartes')
    project.build_depends_on('iso3166') # Country codes converter
    project.build_depends_on('Jinja2') # Path visualizer

    # Suppress Log Output
    logging.disable(logging.CRITICAL)
