"""
Configuration for rcpull to access REDCap projects
"""
import json
import logging
import os

from paths import makedirectory


def add_config(*, config_path: str, key: str, token: str, url: str, path: str):
    """
    Adds the given configuration information to the secrets file in the config
    directory specified by the path.
    """
    makedirectory(config_path)
    file_path = config_file_path(config_path)
    config = get_config(file_path)

    config['projects'][key] = {'token': token, 'url': url, 'path': path}

    if not config['default']:
        config['default'] = key

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(config, indent=2))

    logging.info("New Configuration Added. Current Configuations:")
    show_config(path=config_path)


def config_file_path(path):
    """Constructs path to config file."""
    return os.path.join(path, 'config.json')


def get_config(path):
    """
    Returns the dict from the config file at named path if file exists.
    Otherwise, returns the default empty configuration.
    """
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    return {'projects': {}, 'default': ''}


def get_named_config(*, path: str, key: str = None):
    """Returns the configuration for the named project at the given path.

    Args:
      path - the configuration path
      key - the project key

    Returns:
      The project configuration.

    Raises:
      BadProjectError if no project exists for the key or the default.
    """
    file_path = config_file_path(path)
    config = get_config(file_path)

    if not key:
        key = config["default"]

    if key not in config['projects']:
        raise BadProjectError(key)

    return config['projects'][key]


def show_config(*, path):
    """Prints all named configurations"""
    file_path = config_file_path(path)
    configurations = get_config(file_path)
    print(f"Current (Default) Configuration: {configurations['default']}")
    for name, configuration in configurations['projects'].items():
        print(f"Name: {name}\t"
              f"URL: {configuration['url']}\t"
              f"Local path: {configuration['path']}")


def set_default_instance(path, *, name):
    """Sets the default instance for commands"""
    file_path = config_file_path(path)
    config = get_config(file_path)
    config["default"] = name
    logging.info("Default Configuration is now %s", config["default"])
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(json.dumps(config, indent=2))


class BadProjectError(Exception):
    """Exception for request for non-existent project"""

    def __init__(self, key):
        super().__init__()
        self.instance_name = key
