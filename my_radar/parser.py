# -*- coding:  Utf-8 -*

import os
import sys
from functools import wraps
from .entity import EntityGroup

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
            print("my_radar: {}: {}".format(e.__class__.__name__, str(e)), file=sys.stderr)
            sys.exit(84)
        return output

    return wrapper

class ScriptParser:

    EXTENSION = ".rdr"

    @parse_error_exception
    def __init__(self, path: str, raise_error_file_not_found=True):
        extension = os.path.splitext(path)[1]
        if extension != ScriptParser.EXTENSION:
            raise ScriptParserError("Script extension must be '{}', not '{}'".format(ScriptParser.EXTENSION, extension))
        if not os.path.isfile(path) and raise_error_file_not_found:
            raise FileNotFoundError(path)

        self.__entities = {
            "A": {"list": list(), "size": 6},
            "T": {"list": list(), "size": 3}
        }

        try:
            if os.path.isfile(path):
                with open(path, "r") as file:
                    script = file.read()
            else:
                script = str()
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

        self.__filepath = path

    def update(self, *groups: EntityGroup) -> None:
        for group in groups:
            if group.letter not in self.__entities:
                continue
            self.__entities[group.letter]["list"].clear()
            for entity in group.sprites():
                self.__entities[group.letter]["list"].append(entity.get_setup())

    def save_in_file(self) -> bool:
        try:
            with open(self.__filepath, "w") as file:
                for entity_letter, entity_dict in self.__entities.items():
                    entity_list = entity_dict["list"]
                    for line in entity_list:
                        line = [round(v, 1) for v in line]
                        print(entity_letter, *line, file=file)
        except IOError:
            return False
        return True

    filepath = property(lambda self: self.__filepath)
    airplanes = property(lambda self: self.__entities["A"]["list"])
    towers = property(lambda self: self.__entities["T"]["list"])
