#!/usr/bin/env python2
import requests
import logging
from lxml import html
import textwrap

try:
    import httplib
except ImportError:
    import http.client as httplib

NEWS_HEADLINE_LENGTH = 80
NEWS_DETAILS_LENGTH = 80

class InShortNews(object):
    """Base class for constructing an inshort news query
        Attributes:
            isn_home_URL (str): URL of isn home page.
            isn_more_URL (str): URL of isn more news queries
            host (str): Host name of newsonterminal.
            user_agent (str): User agent to be used for requests calls
            home_page_request_headers (dict): Headers to be used for sending home page request
            more_news_request_headers (dict): Headers to be sent for requesting more news
            headlines_only (bool): Boolean that indicates if only headlines should be shown
            min_news_id (str): Offset of news loaded so far
            print_count (int): Count of headlines displayed
    """
    isn_more_URL = "https://www.inshorts.com/en/ajax/more_news"
    isn_home_URL = "https://www.inshorts.com/en/read"
    host = "www.inshorts.com"
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
    min_news_id = ""
    print_count = 1

    def __init__(self, debug=False, headlines_only=False):
        """Fetch the home page news contents
        Args:
        :param debug: bool that indicates if debug mode is on
        :param headlines_only: bool that indicates if the user wants to see the headlines only
        """
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
        """Display the given news
        Args:
        :param news: A string of news
        :param headline: A bool that indicates if we should display the headline or details of news
        """
        char_count_per_line = NEWS_HEADLINE_LENGTH if headline else NEWS_DETAILS_LENGTH
        for line in textwrap.wrap(news, char_count_per_line, break_long_words=False):
            print line

    def parse_news(self, news_articles):
        """Parse the given news articles to extract the headline, details of news, link to source of news
        and the id of the news item. Iterate over the news articles and generate a list of dictionaries.
        Args:
        :param news_articles: A tree of HTML for parsing
        :return: A list of dictionaries with headline, news details, source of news and news ID
        """
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
        """Print either the headlines or headlines with details in the given list of news items
        Args:
        :param home_page_news_items: List of dictionaries with news items
        """
        if(self.headlines_only):
            self.print_headlines_only(home_page_news_items)
        else:
            self.print_all_news(home_page_news_items)

    def print_headlines_only(self,list_of_news):
        """Print the headlines only in the given list of news items
        Args:
        :param list_of_news: List of news
        """
        for news_item in list_of_news:
            print "["+str(self.print_count)+"] "+news_item['headline']
            print
            self.print_count += 1

    def print_all_news(self, list_of_news):
        """ Print the news headlines along with details of the news and the source of news
        Args:
        :param list_of_news: List of news items
        """
        print "--------------------------------------------------------------------------------"
        for news_item in list_of_news:
            InShortNews.formatted_news(news_item['headline'], True)
            print "--------------------------------------------------------------------------------"
            if not self.headlines_only:
                InShortNews.formatted_news(news_item['headline_description'], False)
                InShortNews.formatted_news(news_item['headline_link'], True)
                print

    def initialize_session(self):
        """ Perform a GET request to fetch the news from the home page and print them
        """
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
        self.min_news_id = tree.xpath('.//script[contains(text(),"min_news_id")]')[0].xpath('.//text()')[0].strip().split(';',1)[0].split("\"")[1]
        self.print_news(home_page_news_items)

    def get_more_news(self):
        """Request for more news using a POST request using an offset of news loaded so far
        """
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