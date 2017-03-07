#!/usr/bin/env python2
import requests
import logging
from lxml import html
from lxml import etree
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
    more_news_request_headers = {
        "Host": host,
        "Connection": "keep-alive",
        "User-Agent": user_agent,
        "Origin": "https://"+host,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "DNT": "1",
        "Referer": "https://www.inshorts.com/en/read",
        "Accept-Encoding": "gzip,deflate,sdch,br",
        "Accept-Language": "en-US,en;q=0.8"
    }
    headlines_only = False
    NEWS_HEADLINE_LENGTH = 80
    NEWS_DETAILS_LENGTH = 80
    min_news_id = ""
    print_count = 1

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

    def parse_news(self, news_articles):
        list_of_homepage_news = [
            {
                'headline': news.xpath('.//span[@itemprop="headline"]')[0].xpath('.//text()')[0],
                'headline_description': news.xpath('.//div[@itemprop="articleBody"]')[0].xpath('.//text()')[0],
                'headline_link': news.xpath('.//a[@class="source"]')[0].get('href').strip(),
                'headline_id': news_articles[0].xpath('.//a[@class="source"]')[0].get('href').strip().split('/', 1)[
                    1].split('/').pop()
            }
            for news in news_articles
            ]
        return list_of_homepage_news

    def print_news(self, home_page_news_items):
        if(self.headlines_only):
            self.print_headlines_only(home_page_news_items)
        else:
            self.print_all_news(home_page_news_items)

    def print_headlines_only(self,list_of_news):
        for news_item in list_of_news:
            # InShortNews.formatted_news(news_item['headline'], True)
            print "["+str(self.print_count)+"] "+news_item['headline']
            self.print_count += 1

    def print_all_news(self, list_of_news):
        print "--------------------------------------------------------------------------------"
        for news_item in list_of_news:
            InShortNews.formatted_news(news_item['headline'], True)
            print "--------------------------------------------------------------------------------"
            if not self.headlines_only:
                InShortNews.formatted_news(news_item['headline_description'], False)
                InShortNews.formatted_news(news_item['headline_link'], True)
                print

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
        home_page_news_items = self.parse_news(news_articles)
        # Finding this looks really manual but we are not left with any other option
        # Using the news_id of the last article for the new loads isn't helping
        # So, let's just work with the way their HTML works
        # CAUTION: Required debugging (Information isn't available)
        self.min_news_id = tree.xpath('.//script[contains(text(),"min_news_id")]')[0].xpath('.//text()')[0].strip().split(';',1)[0].split("\"")[1]
        self.print_news(home_page_news_items)

    def get_more_news(self):
        form_data = {
            "category":"",
            "news_offset": self.min_news_id
        }
        more_news_response = self.isn_request.post(self.isn_more_URL,
                                                   data=form_data,
                                                   headers=self.more_news_request_headers)
        # Update the latest news received
        self.min_news_id = more_news_response.json()['min_news_id']
        news_articles = html.fromstring(more_news_response.json()['html'].strip())
        more_news_articles = self.parse_news(news_articles)
        self.print_news(more_news_articles)