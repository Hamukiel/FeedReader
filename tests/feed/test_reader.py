import unittest
from unittest.mock import patch, MagicMock, call
from xml.etree.ElementTree import ParseError

from requests import RequestException

from src.feed.models import FeedItemDescriptionBlock
from src.feed.reader import FeedReader, FeedParser


class FeedReaderTests(unittest.TestCase):
    """
    TestCase containing tests for the feed Reader and Parser classes.
    """

    @patch('src.feed.reader.requests.get')
    def test_get_content(self, requests):
        """
        In the optimal scenario, we need only to make sure that the requests library is called with the correct inputs,
        and that the returned contents are those also returned by the requests.get, so we mock the library
        """
        url = 'test_url'
        requests.return_value.content = 'test_content'
        requests.return_value.status_code = 200
        res = FeedReader.get_content(url)
        requests.assert_called_with(url=url)
        assert res == requests.return_value.content

    def test_get_content_invalid_url(self):
        """
        We need to make sure that a thrown RequestException is raised if something goes wrong.
        """
        url = 'http://test_url'
        self.assertRaises(RequestException, FeedReader.get_content, url)
        url = 'test_url'
        self.assertRaises(RequestException, FeedReader.get_content, url)

    @patch('src.feed.reader.requests.get')
    def test_get_content_invalid_status_code(self, requests):
        """
        We also need to make sure that a RequestException is raised when a different status_code is returned
        """
        requests.return_value.status_code = 404
        url = 'http://test_url'
        self.assertRaises(RequestException, FeedReader.get_content, url)

    @patch('src.feed.reader.ElementTree.XML')
    def test_get_feed_root(self, xml):
        """
        In the optimal scenario, we only need to make sure that the content is correctly being sent to the
        etree methods, so we mock the ElementTree.
        """
        content = 'test_content'
        FeedReader.get_feed_root(content)
        xml.assert_called_with(content)
        xml.return_value.find.assert_called_with(FeedReader.FEED_ROOT)

    def test_get_feed_root_invalid_content(self):
        """
        If any parsing error occurs, we should make sure that it reaches the outer scope.
        """
        content = 'invalid_content'
        self.assertRaises(ParseError, FeedReader.get_feed_root, content)

    @patch('src.feed.reader.Feed')
    @patch('src.feed.reader.FeedParser.parse_item')
    def test_parse_feed(self, parse_item, feed_cls):
        """
        We should make sure that we are looking for the right tag, sending all results to parse_item and returning a
        Feed object.
        """
        parse_item.side_effect = lambda x: x+1
        items = [1, 2, 3, 4]
        feed = MagicMock()
        feed.findall.return_value = items
        FeedParser.parse_feed(feed)
        feed.findall.assert_called_with(FeedParser.ITEM_TAG)
        parse_item.assert_has_calls([call(item) for item in items])
        feed_cls.assert_called_with([parse_item.side_effect(x) for x in items])

    @patch('src.feed.reader.FeedItem')
    @patch('src.feed.reader.FeedParser.parse_title')
    @patch('src.feed.reader.FeedParser.parse_link')
    @patch('src.feed.reader.FeedParser.parse_description')
    def test_parse_item(self, parse_description, parse_link, parse_title, feeditem_cls):
        """
        We need to make sure that the three content tags are being searched for; the correct tags are being sent to
        their parse_ functions; and that the FeedItem class is being correctly build. We mock everything else.
        """

        item = MagicMock()
        item.find.side_effect = lambda x: x[::-1]
        FeedParser.parse_item(item)
        item.find.assert_has_calls([call(tag) for tag in [FeedParser.TITLE_TAG, FeedParser.LINK_TAG, FeedParser.DESCRIPTION_TAG]])
        parse_title.assert_called_with(item.find.side_effect(FeedParser.TITLE_TAG))
        parse_link.assert_called_with(item.find.side_effect(FeedParser.LINK_TAG))
        parse_description.assert_called_with(item.find.side_effect(FeedParser.DESCRIPTION_TAG))
        feeditem_cls.assert_called_with(parse_title.return_value,
                                        parse_link.return_value,
                                        parse_description.return_value)

    def test_parse_title(self):
        """
        No secrets here. Given an ElementTree element, we must make sure that we are retrieving its text property
        """
        title = MagicMock()
        title.text = 'titulo'
        result = FeedParser.parse_title(title)
        assert result == title.text

    def test_parse_link(self):
        """
        No secrets here. Given an ElementTree element, we must make sure that we are retrieving its text property
        """
        link = MagicMock()
        link.text = 'url'
        result = FeedParser.parse_link(link)
        assert result == link.text

    @patch('src.feed.reader.BeautifulSoup')
    @patch('src.feed.reader.FeedItemDescriptionBlock')
    def test_parse_description(self, block, soup):
        """
        The tricky one. There are 4 base cases we should make sure are working:

        1- A filled paragraph, which is a PARAGRAPH_TAG with actual content;
        2- Images inside DIV_TAGs, which should contain IMG_TAGs with IMG_URL_ATTRB;
        3- Links inside DIV_TAGs, which should contain LINKS_TAGs with a number of URL_TAGs, each with a LINK_REF_ATTRB.
        4- An empty paragraph, which is a PARAGRAPH_TAG without valid content;
        5- Images inside DIV_TAGs, which should contain IMG_TAGs but no IMG_URL_ATTRB;
        6- URL_TAGs without a LINK_REF_ATTRB.

        We are testing whether cases 1-3 have been appended, making sure that cases 4-6 have not.
        """
        def div_side_effect(x):
            if x == FeedParser.IMG_TAG:
                return [{FeedParser.IMG_URL_ATTRB: 'image_url'},
                        {'test': 'invalid_image_url'}]
            if x == FeedParser.LINKS_TAG:
                ul = MagicMock()
                ul.find_all.return_value = [{FeedParser.LINK_REF_ATTRB: 'link_url_1'},
                                            {FeedParser.LINK_REF_ATTRB: 'link_url_2'},
                                            {'test': 'invalid_link_url'}]
                return [ul]
        block.TEXT_TYPE = 'text'
        block.IMAGE_TYPE = 'image'
        block.LINKS_TYPE = 'links'
        soup.return_value = MagicMock()
        empty_paragraph = MagicMock()
        empty_paragraph.name = FeedParser.PARAGRAPH_TAG
        empty_paragraph.get_text.return_value = '\n\xa0\t'
        filled_paragraph = MagicMock()
        filled_paragraph.name = FeedParser.PARAGRAPH_TAG
        filled_paragraph.get_text.return_value = 'abc\n\xa0\tdef'
        div = MagicMock()
        div.name = FeedParser.DIV_TAG
        div.find_all.side_effect = div_side_effect
        soup.return_value.children = [empty_paragraph, filled_paragraph, div]
        description = MagicMock()
        FeedParser.parse_description(description)
        block.assert_called()
        block.assert_has_calls([call(FeedItemDescriptionBlock.TEXT_TYPE, 'abc  def'),
                                call(FeedItemDescriptionBlock.IMAGE_TYPE, 'image_url'),
                                call(FeedItemDescriptionBlock.LINKS_TYPE, ['link_url_1', 'link_url_2'])
                                ])
