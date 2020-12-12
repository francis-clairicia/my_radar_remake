# -*- coding:  Utf-8 -*

import os
import sys
from functools import wraps

class ScriptParserError(BaseException):
    pass

class ScriptLineParserError(ScriptParserError):

    def __init__(self, path: str, line: int, error: str):
        super().__init__("{}, line {}: {}".format(os.path.basename(path), line, error))

def parse_error_exception(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            output = function(*args, **kwargs)
        except (FileNotFoundError, ScriptParserError) as e:
            print("{}: {}".format(e.__class__.__name__, str(e)), file=sys.stderr)
            sys.exit(84)
        return output

    return wrapper

class ScriptParser:

    EXTENSION = ".rdr"

    @parse_error_exception
    def __init__(self, path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        extension = os.path.splitext(path)[1]
        if extension != ScriptParser.EXTENSION:
            raise ScriptParserError("Script extension must be '{}', not '{}'".format(ScriptParser.EXTENSION, extension))

        self.__entities = {
            "A": {"list": list(), "size": 6},
            "T": {"list": list(), "size": 3}
        }

        try:
            with open(path, "r") as file:
                script = file.read()
        except IOError as e:
            raise ScriptParserError("Can't use script file: {}".format(e)) from None

        for index, line in enumerate(script.splitlines(), start=1):
            entity, *infos = line.split()
            if entity not in self.__entities:
                raise ScriptLineParserError(path, index, "Unrecognized entity '{}'".format(entity))
            try:
                infos = [float(value) for value in infos]
            except Exception as e:
                raise ScriptLineParserError(path, index, str(e)) from None
            size = len(infos)
            if size != self.__entities[entity]["size"]:
                raise ScriptLineParserError(path, index, "Expected {} decimal numbers, not {}".format(self.__entities[entity]["size"], size))
            self.__entities[entity]["list"].append(infos)

    airplanes = property(lambda self: self.__entities["A"]["list"])
    towers = property(lambda self: self.__entities["T"]["list"])
