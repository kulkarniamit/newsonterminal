#!/usr/bin/env python2
import requests
import logging
from lxml import html
import textwrap
import json

try:
    import httplib
except ImportError:
    import http.client as httplib

class InShortNews(object):
    """Base class for constructing an In short news query
    """
    isn_more_URL = "https://www.inshorts.com/en/ajax/more_news"
    isn_home_URL = "https://www.inshorts.com/en/read"
    host = "www.inshorts.com"
    # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.14 (KHTML, like Gecko) (Coda, like Safari)"
    user_agent = "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"
    home_page_request_headers = {
        "Host": host,
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": user_agent,
        "Accept": "text/html, application/xhtml+xml,application/xml; q = 0.9,image/webp,*/*;q=0.8",
        "DNT": "1",
        "Accept-Encoding": "gzip,deflate,sdch,br",
        "Accept-Language": "en-US,en;q=0.8,ms;q=0.6",
    }
    headlines_only = False
    NEWS_HEADLINE_LENGTH = 80
    NEWS_DETAILS_LENGTH = 80

    def __init__(self, debug=False, headlines_only=False):
        '''Initialize variables required for all instances'''
        if debug:
            httplib.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
        self.headlines_only  = headlines_only
        self.initialize_session()

    @staticmethod
    def formatted_news(news, headline):
        char_count_per_line = InShortNews.NEWS_HEADLINE_LENGTH if headline else InShortNews.NEWS_DETAILS_LENGTH
        for line in textwrap.wrap(news, char_count_per_line, break_long_words=False):
            print line

    def initialize_session(self):
        # Now, isn_request has cookies with it and we need not attach it every time henceforth
        self.isn_request = requests.Session()
        home_page_response = self.isn_request.get(self.isn_home_URL, headers=self.home_page_request_headers)
        if home_page_response.status_code != 200:
            print ("Failed to fetch the page for some reason")
            print ("Exiting...")
            exit(1)
        tree = html.fromstring(home_page_response.content)
        news_articles = tree.xpath('.//div[@itemtype="http://schema.org/NewsArticle"]');
        list_of_homepage_news = [
            {
                'headline'              : news.xpath('.//span[@itemprop="headline"]')[0].xpath('.//text()')[0],
                'headline_description'  : news.xpath('.//div[@itemprop="articleBody"]')[0].xpath('.//text()')[0],
                'headline_link'         : news.xpath('.//a[@class="source"]')[0].get('href').strip()
            }
                for news in news_articles
            ]
        print "--------------------------------------------------------------------------------"
        for news_item in list_of_homepage_news:
            InShortNews.formatted_news(news_item['headline'], True)
            print "--------------------------------------------------------------------------------"
            if not self.headlines_only:
                InShortNews.formatted_news(news_item['headline_description'], False)
                InShortNews.formatted_news(news_item['headline_link'], True)
                print