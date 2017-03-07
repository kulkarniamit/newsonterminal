#!/usr/bin/env python2
import argparse
from inshortnews_API import *

parser = argparse.ArgumentParser(description='InShort News (Unofficial)',add_help=True)
parser.add_argument('--headlines', action="store_true", default=False, help='Headlines only')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
results = parser.parse_args()

headlines_only_flag = results.headlines


def run():
    isn_object = InShortNews(debug=False, headlines_only = headlines_only_flag)

if __name__ == "__main__":
    run()
