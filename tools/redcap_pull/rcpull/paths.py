"""Module of methods to manage paths and directories"""
import os
import json


def makedirectory(directory_name):
    """
    Creates the directory with the given name.
    Arguments:
      directory_name (String): the name of the directory
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def write_file(*, file_path: str, content: str) -> None:
    """Writes the content to the indicated file in the given path.

    Args:
      file_path: the path to write the file.
      content: the string content of the file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def read_json(*, path):
    """Reads the json file with the given path
    
    Checks that path refers to a file, and 

    Args:
      path: the path to a json file
    
    Returns:
      the object loaded from the file, or None
    """
    if not os.path.isfile(path):
        return None

    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)
