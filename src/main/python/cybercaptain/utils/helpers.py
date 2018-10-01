"""
The helpers module contains functions we define as little helpers. These are desinged to simplify the code.
"""
import os.path
import re
from BTrees.OOBTree import OOBTree # pylint: disable=no-name-in-module
from cybercaptain.utils.jsonFileHandler import json_file_reader
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from hashlib import sha1
from pathlib import Path

def str2bool(v):
    """
    Converts a string to a boolean based on the set rules.

    **Parameters**:
        v : str
            the string that needs convertion.
    **Returns**:
        `True` if the string is either "yes", "true", "t" or "1" else it returns `False`.
    """
    try:
        if v:
            if isinstance(v, bool): return v
            return v.lower() in ("yes", "true", "t", "1")
        return False
    except Exception as exc:
        raise ValueError("Bad value %s" % (v)) from exc

def fileExists(path):
    """
    Checks weather a given path is a file or not. Without the need of importing the os.path in every module.

    **Parameters**:
        path : str
            The path that needs to be checked whether it is a file or not.

    **Returns**:
        `True` if the given path is a file else it returns `False`.
    """
    return os.path.isfile(path)

def is_valid_url(url_to_validate):
    """
    Checks weather a given url is a valid url or not.
    Regex based on django url validation regex:
    https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45 

    **Parameters**:
        url_to_validate : str
            The url that needs to be validated.

    **Returns**:
        `True` if the given url is a valid url. `False` if the url is not valid.
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    return re.match(regex, url_to_validate) is not None

def make_sha1(s, encoding='utf-8'):
    """
    Creates a SHA-1 hash of a given string.

    **Parameters**:
        s : str
            The string to be hashed.
        encoding : str
            Encoding of the given string (Default utf-8)

    **Returns**:
        `str` sha1 hash.
    """
    return sha1(s.encode(encoding)).hexdigest()

def get_file_extension(path_or_file_name):
    """
    Returns the file extension of a path or filename.

    **Parameters**:
        path_or_file_name : str
            The path or filename to receive the extension.

    **Returns**:
        `str` with the extension.
        `''` if no extension was found.
    """
    name, ext = os.path.splitext(path_or_file_name)
    return ext

def append_str_to_filename(path_or_file_name, str_to_append):
    """
    Appends a given string to the given filename.

    **Parameters**:
        path_or_file_name : str
            The path or filename to append to.
        str_to_append: str
            The str to append.

    **Returns**:
        `str` path or filename with the given str appended.
    """
    name, ext = os.path.splitext(path_or_file_name)
    return "{name}{appended}{ext}".format(name=name, appended=str_to_append, ext=ext)

def keyGen(attributes, data):
    """
    Traverses the data and returns the key generated based on the given attributes.

    **Parameters**:
        attributes : list
            A list of attributes which define the key.
        data : dict
            The data for which the key has to be generated for.

    **Returns**:
        `str` with the concatinated attributes as a key.
        `None` if an error occured while finding the key.
    """
    key = ""
    try:
        for attribute in attributes:
            splitSet = attribute.split('.')
            _data = data
            for split in splitSet:
                _data = _data[split]
            key += str(_data)
        return key
    except:
        pass
    return None

def genBTree(src, attributes):
    """
    Generates a B-Tree from the given source file and uses the attributes to generate a key.

    **Parameters**:
        src : str
            the path and file name to the file.
        attributes : list
            the list of attributes which define the key

    **Returns**:
        A complete B-Tree.
    """
    json_fr = json_file_reader(src)
    b_tree = OOBTree()
    while not json_fr.isEOF():
        data = json_fr.readRecord()
        key = keyGen(attributes, data)
        if not key: continue # Key was not generated, go to next
        b_tree.insert(key, data)

    return b_tree