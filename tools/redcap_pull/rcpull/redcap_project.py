"""
Methods for handling project actions.
"""
from typing import Any, List, Mapping
import json
import logging
import os
import re

from paths import makedirectory

def pull(*, reader, project_path: str) -> None:
    """Implements pull actions for the named project.

    Args:
      project_path - the local path to project
      project_name - the project key
    """
    # TODO: handle exception
    metadata = create_project_metadata(reader=reader,
                                       project_path=project_path)
    write_file(path=project_path,
               filename="project.json",
               content=json.dumps(metadata, indent=2))

    project_name = metadata['title'].replace(' ', '')
    # TODO: handle exception
    project_xml = reader.get_project_xml()
    write_file(path=project_path,
               filename=f"{project_name}_project.xml",
               content=project_xml)

    # TODO: handle exception
    project_data_dictionary = reader.get_data_dictionary()
    write_file(path=project_path,
               filename=f"{project_name}_data_dictionary.csv",
               content=project_data_dictionary)

    for instrument in metadata['instruments'].values():
        pull_instrument(reader=reader,
                        name=instrument['instrument'],
                        path=instrument['directory'])


def pull_instrument(*, reader, name: str, path: str) -> None:
    """Pull the data dictionary for the instrument and write to the path.

    Args:
      reader: the PrintReader for the REDCap project.
      name: the name of the instrument.
      path: the local path for writing instrument files.
    """
    logging.info("Pulling instrument %s to directory %s", name, path)
    # TODO: handle exception
    data_dictionary = reader.get_data_dictionary(form=name)
    write_file(path=path, filename="instrument.csv", content=data_dictionary)
    #TODO: need settings.csv content


def choose_directory_name(*, instrument_name: str,
                          directories: List[str]) -> str:
    """Choose a directory name for the instrument.

    Selects options in this order:
    1. Finding a form ID
    2. Removing the prefix 'form_'
    3. the whole instrument name

    Returns:
      a string as candidate for the directory name
    """
    directory_name = instrument_name
    match = re.search('[a-z][0-9][a-z]?', instrument_name)
    if match is not None and match.group(0) not in directories:
        directory_name = match.group(0)
    elif instrument_name.startswith('form_'):
        directory_name = instrument_name.removeprefix('form_')

    return directory_name


def write_file(*, path: str, filename: str, content: str) -> None:
    """Writes the content to the indicated file in the given path.

    Args:
      path: the path to write the file.
      filename: the name of the file.
      content: the string content of the file.
    """
    file_path = os.path.join(path, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def create_project_metadata(*, reader, project_path: str) -> Mapping[str, Any]:
    """Creates the metadata object for the project.

    Args:
      reader: the ProjectReader for the project.

    Raises:
      REDCapConnectionError if requests fail.
    """
    directories = list_directories(project_path)
    # TODO: handle exception
    project_info = reader.get_project_info()
    metadata = {'title': project_info['project_title'], 'instruments': {}}
    # TODO: handle exception
    instruments = reader.get_instruments()
    matching_names = match_instrument_directories(instrument_list=instruments,
                                                  directory_list=directories)
    for name, directory_list in matching_names.items():
        if len(directory_list) > 1:
            logging.error("Instrument name %s matches more than one directory",
                          name)
            for directory in directory_list:
                logging.error("Matching directory: %s", directory)
            # TODO: raise exception ?
            continue

        if len(directory_list) == 0:
            directory = choose_directory_name(instrument_name=name,
                                              directories=directory_list)
            if directory in directories:
                logging.error("Can't create directory name for instrument %s",
                              name)
                continue

            logging.info("Creating directory %s for instrument %s", directory,
                         name)
            instrument_path = os.path.join(project_path, directory)
            makedirectory(instrument_path)
        else:
            directory = directory_list[0]
            instrument_path = os.path.join(project_path, directory)

        metadata['instruments'][directory] = {
            'directory': os.path.join(project_path, directory),
            'instrument': name
        }

    return metadata


def list_directories(path) -> List[str]:
    """Returns the list of subdirectories of the directory at the path.

    Args:
      path: the path of the parent directory.

    Returns:
      the list of subdirectory names
    """
    directories = list()
    with os.scandir(path=path) as directory:
        for entry in directory:
            if not entry.name.startswith('.') and entry.is_dir():
                directories.append(entry.name)
    return directories


def match_instrument_directories(*, instrument_list: List[Mapping[str, str]],
                                 directory_list: List[str]) -> Mapping[str,List[str]]:
    """Returns directories whose names are substrings of the instrument names.

    Args:
      instrument_list: the list of instruments
      directory_list: the list of directories

    Returns:
      Map of instrument names to lists of matching directory names
    """
    instrument_map = dict()
    for instrument in instrument_list:
        instrument_name = instrument['instrument_name']
        matches = [name for name in directory_list if name in instrument_name]
        instrument_map[instrument_name] = matches

    return instrument_map
