#!/usr/bin/env python2
import argparse
from inshortnews_API import *

parser = argparse.ArgumentParser(description='InShort News (Unofficial)',add_help=True)
parser.add_argument('--headlines', action="store_true", default=False, help='Headlines only')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
results = parser.parse_args()
headlines_only_flag = results.headlines

def run():
    """ Display the home page news and interactively load more news based on user input
    """
    isn_object = InShortNews(debug=False, headlines_only = headlines_only_flag)
    while 1:
        load_more_news = raw_input("Load more news [y/n]: ")
        if load_more_news == 'y' or load_more_news == 'Y' or load_more_news == "":
            isn_object.get_more_news()
        else:
            break

if __name__ == "__main__":
    run()