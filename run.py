#! /bin/python3
# -*- coding: Utf-8 -*

import sys
import argparse
from my_radar import MyRadar, ScriptParser

class MyHelpFormatter(argparse.RawTextHelpFormatter):

    def format_help(self) -> str:
        help_str = super().format_help()
        if len(help_str.splitlines()) == 1:
            return help_str
        nb_spaces = 4
        user_interaction_help = [
            "user interactions:",
            "  'L' key:" + nb_spaces * " " + "enable/disable hitboxes and areas",
            "  'S' key:" + nb_spaces * " " + "enable/disable sprites",
            "  'P' key:" + nb_spaces * " " + "Play/pause the simulation",
        ]
        return help_str + "\n" + "\n".join(user_interaction_help) + "\n"

def main() -> int:
    parser = argparse.ArgumentParser(prog="my_radar", description="Air traffic simulation panel", formatter_class=MyHelpFormatter)
    parser.add_argument("script", help="Path to a .rdr script file")
    parser.add_argument("-e", "--editor", help="Launch the script editor", action="store_true")

    args = parser.parse_args()
    script = ScriptParser(args.script, raise_error_file_not_found=not args.editor)

    MyRadar(script, editor=args.editor).start()
    return 0

if __name__ == "__main__":
    sys.exit(main())
