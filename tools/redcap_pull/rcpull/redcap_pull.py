"""
Script to pull projects for sharing.
"""

import argparse
from distutils.command.config import config
import logging
import os

from rcpull.config import (
    add_config,
    set_default_instance,
    show_config
)
from rcpull.project import pull


logging.basicConfig(level=logging.INFO)


def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help(sys.stderr)


def get_argument_parser():
    """
    """
    parser = argparse.ArgumentParser(
        description="Pull projects from REDCap for sharing"
    )
    subparsers = parser.add_subparsers(title="subcommands")

    # configuration commands
    parser_config = subparsers.add_parser("configure")
    config_subparsers = parser_config.add_subparsers()

    # add configuration
    parser_add = config_subparsers.add_parser(
        "add",
        help="Add/update REDCap access configuration"
    )
    add_config_arguments(parser_add)
    parser_add.set_defaults(func=do_config_add)

    # set default configuration
    parser_default = config_subparsers.add_parser(
        "set-default",
        help="set default login configuration"
    )
    parser_default.add_argument(
        '-n',
        '--name',
        help="the name of the default login configuration",
        default="local"
    )
    parser_default.set_defaults(func=do_config_default)

    # display configurations
    parser_show = config_subparsers.add_parser(
        'show',
        help='show all configurations'
    )
    parser_show.set_defaults(func=do_config_show)

    # pull command
    parser_pull = subparsers.add_parser("pull")
    add_component_arguments(parser_pull, action="pull")
    parser_pull.set_defaults(func=do_pull)

    return parser


def add_config_arguments(parser):
    """Adds optional args for configuration subparser"""
    parser.add_argument(
        '-n', "--name",
        help="the name to use for the project instance"
    )
    parser.add_argument(
        "-t", "--token",
        help="the access token for the project"
    )
    parser.add_argument(
        "-u", "--url",
        help="the URL for the REDCap instance"
    )


def config_path():
    return os.path.normpath(
        os.path.join(os.environ.get('SCRIPT_DIR'), 'config')
    )


def do_config_add(args):
    """Add new configuration"""
    add_config(
        path=config_path(),
        key=args.name,
        token=args.token,
        url=args.url
    )


def do_config_default(args):
    set_default_instance(config_path(), name=args.name)


def do_config_show(args):
    show_config(path=config_path())


def add_component_arguments(parser, *, action):
    """Adds optional arguments for project component subparsers"""
    parser.add_argument(
        "-a", "--all",
        help="pull all files in a project",
        action="store_true"
    )

    parser.add_argument(
        "-d", "--directory",
        help="working directory for the command. optional for Pull (default is current directory).",
        required=(action == 'push'),
        default=os.getcwd()
    )

    parser.add_argument(
        "-n", "--name",
        help="configuration name",
        type=str
    )

def do_pull(args):
    path = os.path.normpath(args.directory)

    if args.all:
        project.pull(path=path)
        return

    logging.error(
        'Choose an option for what to pull'
    )

if __name__ == "__main__":
    main()