#! /bin/python3
# -*- coding: Utf-8 -*

import sys
from my_radar import MyRadar

def main() -> int:
    MyRadar().start()
    return 0

if __name__ == "__main__":
    sys.exit(main())