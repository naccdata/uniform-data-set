"""
Configuration for rcpull to access REDCap projects
"""
import json
import logging
import os

from rcpull.paths import makedirectory


def add_config(*, path, key, token, url):
    """
    Adds the given configuration information to the secrets file in the config
    directory specified by the path.
    """
    makedirectory(path)
    file_path = config_file_path(path)
    config = get_config(file_path)

    config['instances'][key] = {
        'token': token,
        'url': url
    }

    with open(file_path, 'w') as file:
        file.write(json.dumps(config, indent=2))

    logging.info("New Configuration Added. Current Configuations:")
    show_config(path=path)

def config_file_path(path):
    return os.path.join(path, 'config.json')

def get_config(path):
    """
    Returns the dict from the config file at named path if file exists.
    Otherwise, returns the default.
    """
    if os.path.isfile(path):
        with open(path) as file:
            return json.load(file)

    return {}


def show_config(*, path):
    """Prints all named configurations"""
    file_path = config_file_path(path)
    configurations = get_config(file_path)
    print(f"Current (Default) Configuration: {configurations['default']}")
    for name, configuration in configurations["instances"].items():
        print("Name: {}\tToken: {}\t URL: {}".format(
            name, configuration["token"], configuration["url"]))


def set_default_instance(path, *, name):
    file_path = config_file_path(path)
    config = get_config(file_path)
    config["default"] = name
    logging.info("Default Configuration is now %s", config["default"])
    with open(file_path, 'w') as file:
        file.write(json.dumps(config, indent=2))