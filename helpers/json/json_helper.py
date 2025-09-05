"""
This module provides utility functions for reading, writing,
and processing data in JSON format.

Functions:
    - read_json_data(path): Reads JSON data from a specified file.
    - write_json_data(path, data): Writes dictionary data to a JSON file.
"""


import json


ENCODING = "utf-8"


def read_json_data(path):
    """Read and parse JSON data from a file, returning a dict or None if not found."""
    try:
        with open(path, "r", encoding=ENCODING) as file:
            json_str = file.read()
            data = json.loads(json_str)
        return data
    except FileNotFoundError as error:
        print(f"File not found: {path}", error)
        return None


def write_json_data(path, data):
    """Write a dictionary as JSON to the specified file path."""
    try:
        with open(path, "w", encoding=ENCODING) as file:
            json_str = json.dumps(data)
            file.write(json_str)
    except FileExistsError as error:
        print(f"File already exists: {path}", error)
