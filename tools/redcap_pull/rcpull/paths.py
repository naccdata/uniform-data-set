"""Module of methods to manage paths and directories"""
import os


def makedirectory(directory_name):
    """
    Creates the directory with the given name.
    Arguments:
      directory_name (String): the name of the directory
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
