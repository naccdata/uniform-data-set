"""
Methods for handling project actions.
"""
from typing import Any, List, Mapping
import logging
import os
import re

from paths import makedirectory, write_file
from redcap_connection import REDCapConnectionError
import project_metadata


def pull_metadata(*, reader, project_path: str) -> None:
    """Creates project metadata for the project.
    
    Args:
      reader: the project reader for the project
      project_path: the path for the project files
    """
    metadata = create_project_metadata(reader=reader,
                                       project_path=project_path)
    if not metadata:
        logging.error("Failed to create project")
        return

    project_metadata.write_metadata(project_path=project_path,
                                    metadata=metadata)


def pull(*, reader, project_path: str) -> None:
    """Implements pull actions for the named project.

    Args:
      project_path - the local path to project
      project_name - the project key
    """
    makedirectory(project_path)
    metadata = project_metadata.get_metadata(project_path=project_path)
    if not metadata:
        try:
            metadata = create_project_metadata(reader=reader,
                                               project_path=project_path)
        except REDCapConnectionError as error:
            logging.error("Could not retrieve project information\n%s", error)
            return

    project_name = metadata['title'].replace(' ', '').replace(':', '')

    try:
        project_xml = reader.get_project_xml()
    except REDCapConnectionError as error:
        logging.error("Could not retrieve project XML\n%s", error)
        return

    write_file(file_path=os.path.join(project_path,
                                      f"{project_name}.REDCap.xml"),
               content=project_xml)

    try:
        project_data_dictionary = reader.get_data_dictionary()
    except REDCapConnectionError as error:
        logging.error("Could not retrieve project information\n%s", error)
        return

    write_file(file_path=os.path.join(project_path,
                                      f"{project_name}_data_dictionary.csv"),
               content=project_data_dictionary)

    for instrument in metadata['instruments'].values():
        path = os.path.join(project_path, instrument['directory'])
        download_instrument(reader=reader,
                            name=instrument['instrument'],
                            path=path)


def pull_instrument(*, reader, instrument: str, path: str) -> None:
    """Pull the instrument to the project files.
    
    Args:
      reader: the ProjectReader for the project
      name: the name of the instrument
      path: the local path for writing instrument files
    """
    instrument_obj = project_metadata.get_instrument(project_path=path,
                                                     key=instrument)
    file_path = os.path.join(path, instrument['directory'])
    download_instrument(reader=reader,
                        name=instrument_obj['instrument'],
                        path=file_path)


def download_instrument(*, reader, name: str, path: str) -> None:
    """Pull the data dictionary for the instrument and write to the path.

    Args:
      reader: the PrintReader for the REDCap project.
      name: the name of the instrument.
      path: the local path for writing instrument files.
    """
    logging.info("Pulling instrument %s to directory %s", name, path)
    try:
        data_dictionary = reader.get_data_dictionary(form=name)
    except REDCapConnectionError as error:
        logging.error("Unable to pull instrument %s\n%s", name, error)
        return

    write_file(file_path=os.path.join(path, "instrument.csv"),
               content=data_dictionary)
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


def create_project_metadata(*, reader, project_path: str) -> Mapping[str, Any]:
    """Creates a metadata object for the project

    Pulls project information from REDCap using the project reader, and
    creates the project directory and metadata.

    Args:
      reader: the ProjectReader for the project.

    Returns:
        The metadata object if created, None otherwise
    """

    try:
        project_info = reader.get_project_info()
    except REDCapConnectionError as error:
        logging.error("Could not retrieve project information\n%s", error)
        return None

    metadata = project_metadata.create_metadata(
        title=project_info['project_title'])

    try:
        instruments = reader.get_instruments()
    except REDCapConnectionError as error:
        logging.error("Could not retrieve project instruments\n%s", error)
        return None

    directories = list_directories(project_path)
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
            # TODO: move this out to avoid sideeffects (?)
            makedirectory(instrument_path)
        else:
            directory = directory_list[0]

        project_metadata.add_instrument_object(metadata=metadata,
                                               key=directory,
                                               instrument=name,
                                               directory=directory)

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


def match_instrument_directories(
        *, instrument_list: List[Mapping[str, str]],
        directory_list: List[str]) -> Mapping[str, List[str]]:
    """Returns directories whose names are substrings of the instrument names.

    Args:
      instrument_list: the list of instruments
      directory_list: the list of directories

    Returns:
      Map of instrument names to lists of matching directory namess
    """
    instrument_map = dict()
    for instrument in instrument_list:
        instrument_name = instrument['instrument_name']
        matches = [name for name in directory_list if name in instrument_name]
        instrument_map[instrument_name] = matches

    return instrument_map
