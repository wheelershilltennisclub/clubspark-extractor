"""
Contains reusable classes and functions for the cs-membership-list-extractor script.
"""

import sys


def quit_with_error(error_msg):
    print(f"Error: {error_msg}", file=sys.stderr)
    sys.exit(1)


def get_bordered_string(string, char='-'):
    border = char * len(string)
    return f"{border}\n{string}\n{border}"
