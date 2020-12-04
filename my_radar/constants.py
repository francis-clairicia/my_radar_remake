# -*- coding: Utf-8 -*

import os.path
import sys
from typing import Callable
from pygame import Color

WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
GRAY = Color(127, 127, 127)
GRAY_DARK = Color(95, 95, 95)
GRAY_LIGHT = Color(175, 175, 175)
RED = Color(255, 0, 0)
RED_DARK = Color(195, 0, 0)
RED_LIGHT = Color(255, 100, 100)
ORANGE = Color(255, 175, 0)
YELLOW = Color(255, 255, 0)
GREEN = Color(0, 255, 0)
GREEN_DARK = Color(0, 128, 0)
GREEN_LIGHT = Color(128, 255, 128)
CYAN = Color(0, 255, 255)
BLUE = Color(0, 0, 255)
BLUE_DARK = Color(0, 0, 128)
BLUE_LIGHT = Color(128, 128, 255)
MAGENTA = Color(255, 0, 255)
PURPLE = Color(165, 0, 255)
TRANSPARENT = Color(0, 0, 0, 0)

def __set_constant_path(path_exists: Callable[[str], bool], path: str, *paths: str, special_msg=None, raise_error=True) -> str:
    all_path = os.path.join(path, *paths)
    if not os.path.isabs(all_path):
        all_path = os.path.join(sys.path[0], all_path)
    if not path_exists(all_path) and raise_error:
        if special_msg:
            raise FileNotFoundError(special_msg)
        raise FileNotFoundError(f"{all_path} folder not found")
    return all_path

def set_constant_directory(path, *paths, special_msg=None, raise_error=True) -> str:
    return __set_constant_path(os.path.isdir, path, *paths, special_msg=special_msg, raise_error=raise_error)

def set_constant_file(path, *paths, special_msg=None, raise_error=True) -> str:
    return __set_constant_path(os.path.isfile, path, *paths, special_msg=special_msg, raise_error=raise_error)

RESOURCES_FOLDER = set_constant_directory("resources", special_msg="Resources folder not present")
IMG_FOLDER = set_constant_directory(RESOURCES_FOLDER, "img", special_msg="Images folder not present")
FONT_FOLDER = set_constant_directory(RESOURCES_FOLDER, "font", special_msg="Fonts folder not present")

IMG = {
    "airplane": set_constant_file(IMG_FOLDER, "airplane.png"),
    "tower": set_constant_file(IMG_FOLDER, "tower.png"),
    "world_map": set_constant_file(IMG_FOLDER, "world_map.jpg")
}

FONT_DARK_CALIBRI = set_constant_file(FONT_FOLDER, "Darks_Calibri_Remix.ttf")

AIRPLANE_SIZE = (20, 20)
