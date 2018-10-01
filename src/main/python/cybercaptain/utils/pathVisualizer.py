import os
import datetime
import logging
from jinja2 import Template

logger = logging.getLogger("CyberCaptain")

def run_path_visualisation(paths, config, modulesConfig):
    """
    Runs the path visualization. Assembles the paths to be visualized.
    Will call the render function to output a HTML. 

    **Parameters**:
        paths : list
            List of the paths found from the run algorithm.
        config : obj
            The script config object.
        modulesConfig : obj
            The module config object.

    """
    all_targets = [os.path.basename(config[s]["target"]) for s in config.sections]
    all_target_tasks = {os.path.basename(config[s]["target"]):s for s in config.sections}
    
    added_tasks = []
    prepared_paths = []
    for path in paths:
        prepared_tasks = []
        for idx, task in enumerate(list(reversed(path))):
            s_module, s_name, *identifier = task.split(" ")

            # Special Rule For Join Module To Have A Connection To Another Module
            special_connection = False
            if s_module == "processing_join":
                args = config[task]
                con_module, con_name, *identifier = all_target_tasks.get(os.path.basename(args["joinwith"]), s_module+"_SPECIAL "+s_name+"_SPECIAL").split(" ")
                special_connection = {
                    "connection_to_module" : con_module,
                    "connection_to_name" : con_name,
                    "will_be_created" : (os.path.basename(args["joinwith"]) in all_targets)
                }

            prepared_tasks.append({
                'module':s_module,
                'name':s_name,
                'display': (task not in added_tasks),
                'specialConnection': special_connection,
                'last': (idx == len(path) - 1),
                'attributes': config[task]
            })
            added_tasks.append(task)
        prepared_paths.append(prepared_tasks)
    logger.debug("Path prepared for visualization!")
    render_path_visualisation(config['projectRoot'], config['projectName'], prepared_paths)

def render_path_visualisation(projectRoot, configName, prepared_paths):
    """
    Renders the given prepared paths to the HTML template.
    The rendere HTML will be written to the projectRoot location.

    **Parameters**:
        projectRoot : str
            The configured project path to write to.
        configName : dict
            The configured project name.
        prepared_paths : list
            A list of the prepared paths.
    """
    with open(os.path.join(os.path.dirname(__file__), 'assets/visualizer_template.html')) as file_:
        template = Template(file_.read())
    
    visuFileName = "pathvisualizer_%s.html" % configName.replace(" ","")
    visuFilePath = os.path.join(projectRoot, visuFileName)
    renderedTemplate = template.render(configName=configName, currentDate=datetime.datetime.now(), paths=prepared_paths)
    with open(visuFilePath,'w') as f:
        f.write(renderedTemplate)

    logger.info("Path visualized - find the file at %s" % visuFilePath)