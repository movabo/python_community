# -*- coding: utf-8 -*-

"""Walk through directories and open the desired file / directory.
(Only works with unix-systems.)

Usage: / or ~/
Examples: /home/xyz/Pictures
          ~/Pictures
"""

from albertv0 import *
import os
import traceback

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Directory Walker"
__version__ = "1.0"
__author__ = "Moritz Bock"
__dependencies__ = ["xdg-open"]

home = os.path.expanduser('~')
"""Home directory of the user."""

icons = {
    "file": "{}/file.svg".format(os.path.dirname(__file__)),
    "directory": "{}/directory.svg".format(os.path.dirname(__file__))
}
"""Icons for files and directories."""

OPEN = "xdg-open"
"""Command line argument to open a file."""


def contractuser(path):
    """Replace the home directory part of a path with a '~'.

    Args:
        path (str): Path to be contracted.

    Returns:
        str: Contracted path.
    """
    return path.replace(home, "~")


def validPath(string):
    """Check if a string is a valid file system path.
    (Only works on unix.)

    Args:
        string (str): String to check if it is a valid path.

    Returns:
        bool: True if it is a valid path, else False.
    """
    if len(string) is 0:
        return
    return string[0] in ("~", os.sep)


def buildItem(path,
              file=False):
    """Build an item to show in albert.

    Args:
        path (str): Path of the file or directory.
        file (str, optional): If the path belongs to a file, the file
            name.

    Returns:
        Item: Item representing the file or directory.
    """
    home_path = contractuser(path)
    if file:
        action_string = "Open file {}".format(file)
    else:
        action_string = "Open directory {}".format(home_path)
    item = Item(id=__prettyname__, completion=home_path)
    item.text = home_path
    item.subtext = action_string
    item.addAction(ProcAction(text=action_string,
                              commandline=[OPEN, path]))
    item.icon = icons["file"] if file else icons["directory"]
    return item


def run(query):
    """Run the script to search if the query matches a path.

    Args:
        query (Query): Query object representing the current query
            execution.

    Returns:
        list or None: Items of the converted colors.
    """
    if not validPath(query.rawString):
        return
    path = os.path.expanduser(query.rawString)

    files = []
    dir, file = os.path.split(path)
    is_dir = False

    # Check if the full string matches a file or dir
    if os.path.isfile(path):
        files.append(buildItem(path, file))
    elif os.path.isdir(path) and file != ".":
        dir = path
        if not dir.endswith(os.sep):
            dir += os.sep
        files.append(buildItem(dir))
        is_dir = True

    # Add all files in the current directory starting with
    # the file-part of the user submitted query
    for dir_file in os.listdir(dir):
        if dir_file == file:
            continue
        if is_dir or dir_file.startswith(file):
            dir_file_path = os.path.join(dir, dir_file)
            if os.path.isfile(dir_file_path):
                files.append(buildItem(dir_file_path, dir_file))
            else:
                files.append(buildItem(dir_file_path + os.sep))

    return files


def handleQuery(query):
    """Run the script to search if the query matches a path.

    Args:
        query (Query): Query object representing the current query
            execution.

    Returns:
        list or None: Items of the converted colors.
    """
    try:
        return run(query)
    except Exception as e:
        critical(''.join(traceback.format_exception(etype=type(e),
                 value=e,
                 tb=e.__traceback__)))
