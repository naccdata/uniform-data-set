"""Project metadata handling.

Inspired by configs.py
"""
import json
import logging
import os
import paths


def create_metadata(*, title: str):
    return {'title': title, 'instruments': {}}


def create_instrument(*, instrument: str, directory: str):
    return {'instrument': instrument, 'directory': directory}


def add_instrument_object(*, metadata, key: str, instrument: str,
                          directory: str):
    metadata['instruments'][key] = create_instrument(instrument=instrument,
                                                     directory=directory)


def add_instrument(*, project_path: str, key: str, instrument: str,
                   directory: str):
    """Adds an instrument to the project metadata"""
    paths.makedirectory(project_path)
    metadata = get_metadata(project_path)

    if not metadata:
        logging.error("Cannot add instrument to project at %s", project_path)
        return

    add_instrument_object(metadata=metadata,
                          key=key,
                          instrument=instrument,
                          directory=directory)

    write_metadata(project_path=project_path, metadata=metadata)


def metadata_file_path(path):
    """Builds path to project file."""
    return os.path.join(path, 'project.json')


def get_metadata(project_path):
    """Returns the dict from the named path if the file exists.
    Otherwise, returns None"""
    file_path = metadata_file_path(project_path)
    return paths.read_json(path=file_path)


def write_metadata(*, project_path, metadata):
    file_path = metadata_file_path(project_path)
    paths.write_file(file_path=file_path,
                     content=json.dumps(metadata, indent=2))


def get_instrument(*, project_path: str, key: str):
    """Returns the metadata for the named instrument at the given path.

    Args:
      project_path: the path to the project
      key: the key for the instrument

    Returns:
      the metadata for the instrument, or None if not found
    """
    if not key:
        return None

    file_path = metadata_file_path(project_path)
    metadata = get_metadata(file_path)

    if key not in metadata['instruments']:
        return None

    return metadata['instruments'][key]
