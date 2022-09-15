"""
Script to pull projects for sharing.
"""

import argparse
import logging
import os
import sys

from config import (add_config, get_named_config, set_default_instance,
                    show_config)
from redcap_connection import ProjectReader, REDCapConnectionError
from redcap_project import pull, pull_metadata, pull_instrument

logging.basicConfig(level=logging.INFO)


def main():
    """Main method to run script."""
    parser = get_argument_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help(sys.stderr)


def get_argument_parser():
    """
    Creates the parser for capturing command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Pull projects from REDCap for sharing")
    subparsers = parser.add_subparsers(title="subcommands")

    # configuration commands
    parser_config = subparsers.add_parser("configure")
    config_subparsers = parser_config.add_subparsers()

    # add configuration
    parser_add = config_subparsers.add_parser(
        "add", help="Add/update REDCap access configuration")
    add_config_arguments(parser_add)
    parser_add.set_defaults(func=do_config_add)

    # set default configuration
    parser_default = config_subparsers.add_parser(
        "set-default", help="set default login configuration")
    parser_default.add_argument(
        '-n',
        '--name',
        help="the name of the default login configuration",
        default="local")
    parser_default.set_defaults(func=do_config_default)

    # display configurations
    parser_show = config_subparsers.add_parser('show',
                                               help='show all configurations')
    parser_show.set_defaults(func=do_config_show)

    # pull command
    parser_pull = subparsers.add_parser("pull")
    add_component_arguments(parser_pull, action="pull")

    parser_pull.set_defaults(func=do_pull)

    return parser


def add_config_arguments(parser):
    """Adds optional args for configuration subparser"""
    parser.add_argument('-n',
                        "--name",
                        help="the name to use for the project instance")
    parser.add_argument("-t",
                        "--token",
                        help="the access token for the project")
    parser.add_argument("-u", "--url", help="the URL for the REDCap instance")
    parser.add_argument("-p", "--path", help="the local path of the project")


def config_path():
    """Constructs the path for the configuration directory.

    The directory is located in the directory indicated by the `SCRIPT_DIR`
    environment variable.

    Returns:
      Path for the configuration directory.
    """
    directory = os.environ.get('SCRIPT_DIR')
    if directory is None:
        directory = ''
    return os.path.normpath(os.path.join(directory, 'config'))


def do_config_add(args):
    """Add new configuration"""
    add_config(config_path=config_path(),
               key=args.name,
               token=args.token,
               url=args.url,
               path=os.path.expanduser(args.path))


def do_config_default(args):
    """Action function for setting default project."""
    set_default_instance(config_path(), name=args.name)


def do_config_show(args):
    """Action function for showing defined project configurations."""
    # pylint: disable=unused-argument
    show_config(path=config_path())


def add_component_arguments(parser, *, action):
    """Adds optional arguments for project component subparsers"""
    parser.add_argument(
        "-d",
        "--directory",
        help=
        "working directory for the command. optional for Pull (default is current directory).",
        required=(action == 'push'),
        default=os.getcwd())

    parser.add_argument("-n", "--name", help="configuration name", type=str)
    parser.add_argument("-i",
                        "--instrument",
                        help=f"the instrument to {action}",
                        type=str)
    parser.add_argument("-m",
                        "--metadata",
                        help=f"{action} the project metadata",
                        action='store_true')


def do_pull(args) -> None:
    """Action function for performing pull.

    Args:
      args: the command line arguments for pulling.
    """
    name = None
    if args.name:
        name = args.name

    configuration = get_named_config(path=config_path(), key=name)
    reader = ProjectReader.create(token=configuration['token'],
                                  url=configuration['url'])
    path = configuration['path']

    if args.metadata:
        pull_metadata(reader=reader, project_path=path)
        return

    if args.instrument:
        pull_instrument(reader=reader, path=path, instrument=args.instrument)

    try:
        pull(reader=reader, project_path=path)
    except REDCapConnectionError as error:
        logging.error("%s\n%s", error.message, error.error)


if __name__ == "__main__":
    main()
