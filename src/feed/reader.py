from xml.etree.ElementTree import ParseError

import requests
from xml.etree import ElementTree
from bs4 import BeautifulSoup
from requests import RequestException
from werkzeug.exceptions import BadRequest

from src.feed.models import FeedItem, FeedItemDescriptionBlock, Feed


class FeedParser:
    """
    Class containing static methods related to parsing a feed's contents and returning the corresponding model classes.
    """

    TITLE_TAG = 'title'
    LINK_TAG = 'link'
    DESCRIPTION_TAG = 'description'

    PARAGRAPH_TAG = 'p'
    DIV_TAG = 'div'
    IMG_TAG = 'img'
    LINKS_TAG = 'ul'
    URL_TAG = 'a'
    IMG_URL_ATTRB = 'src'
    LINK_REF_ATTRB = 'href'
    ITEM_TAG = 'item'
    PARSER = 'html.parser'

    @staticmethod
    def parse_feed(feed):
        """
        Method responsible for parsing a feed's contents, given its ElementTree data root.

        :param feed: Feed's data root, as an ElementTree
        :return: A parsed Feed object
        """
        items = feed.findall(FeedParser.ITEM_TAG)
        return Feed([FeedParser.parse_item(item) for item in items])

    @staticmethod
    def parse_item(item):
        """
        Method responsible for parsing an item contained in a feed, given it's ElementTree root.

        :param item: Item's root, as an ElementTree
        :return: A parsed FeedItem object
        """
        title = item.find(FeedParser.TITLE_TAG)
        link = item.find(FeedParser.LINK_TAG)
        description = item.find(FeedParser.DESCRIPTION_TAG)
        return FeedItem(FeedParser.parse_title(title),
                        FeedParser.parse_link(link),
                        FeedParser.parse_description(description))

    @staticmethod
    def parse_title(title):
        """
        Method responsible for parsing a feed's title, given its Element.

        :param title: Element containing the title.
        :return: Parsed title text.
        """
        return title.text

    @staticmethod
    def parse_link(link):
        """
        Method responsible for parsing a feed's link, given its Element.

        :param link: Element containing the link.
        :return: Parsed link
        """
        return link.text

    @staticmethod
    def parse_description(description):
        """
        Method responsible for parsing an item's description, given its Element. It obeys the following rules:

        - PARAGRAPH_TAGs are parsed as TEXT_TYPE description blocks, containing the tags' text content;
        - IMG_TAGs inside DIV_TAGs are parsed as IMAGE_TYPE description blocks, containing the tags' image URLs;
        - LINKS_TAG inside DIV_TAGs are parsed as LINKS_TYPE description blocks, containing a list with all of the
        tags' URLs

        :param description: Element containing the feed item's description.
        :return: A list of parsed FeedItemDescriptionBlock objects
        """
        soup = BeautifulSoup(description.text, FeedParser.PARSER)
        res = []
        for child in soup.children:
            if child.name == FeedParser.PARAGRAPH_TAG:
                txt = child.get_text("", strip=False).replace('\n', '').replace('\xa0', ' ').replace('\t', ' ').lstrip()
                if txt.strip() != '':
                    res.append(FeedItemDescriptionBlock(FeedItemDescriptionBlock.TEXT_TYPE, txt))
            elif child.name == FeedParser.DIV_TAG:
                for img in child.find_all(FeedParser.IMG_TAG):
                    # We are going for a LBYL approach, since we do not have a reliable logging solution in place
                    if FeedParser.IMG_URL_ATTRB in img:
                        res.append(FeedItemDescriptionBlock(FeedItemDescriptionBlock.IMAGE_TYPE,
                                                            img[FeedParser.IMG_URL_ATTRB]))
                for ul in child.find_all(FeedParser.LINKS_TAG):
                    res.append(FeedItemDescriptionBlock(FeedItemDescriptionBlock.LINKS_TYPE,
                                                        [a[FeedParser.LINK_REF_ATTRB]
                                                         for a in ul.find_all(FeedParser.URL_TAG)
                                                         if FeedParser.LINK_REF_ATTRB in a]))
        return res


class FeedReader:
    """
    Class containing static methods for getting a feed's contents and preparing those for parsing
    """

    FEED_ROOT = 'channel'

    @staticmethod
    def get_content(url):
        """
        Method responsible for retrieving a feed's content. If it fails to retrieve it, it will raise a generic
        RequestException.

        :param url: Feed's complete url
        :return: Requested feed's contents.
        """
        res = requests.get(url=url)
        if res.status_code != 200:
            raise RequestException(f"The requested feed could not be retrieved. Code: {res.status_code}")
        return res.content

    @staticmethod
    def get_feed_root(content):
        """
        Method responsible for finding the feed's data root element, which is assumed to be the FEED_ROOT constant.
        Any thrown ParseErrors should reach the outer scope.

        :param content: Feed's contents, as a string
        :return: Feed's data root as an ElementTree, ready for parsing.
        """
        root = ElementTree.XML(content)
        return root.find(FeedReader.FEED_ROOT)
