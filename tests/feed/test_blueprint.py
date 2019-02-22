import json
import unittest
from unittest.mock import patch
from xml.etree.ElementTree import ParseError

from requests import RequestException

from src.app import create_app


class FeedBlueprintTests(unittest.TestCase):
    """
    TestCase containing tests for the FeedReader's API route.
    """

    def setUp(self):
        """
        Setting up a Flask app for testing.
        """
        self.app = create_app()
        self.app.config['TESTING'] = True

    @patch('src.feed.blueprint.FeedReader')
    @patch('src.feed.blueprint.FeedParser')
    def test_read_feed(self, parser, reader):
        """
        We should make sure that return values are correcly moved around as parameters to each call, and that the
        results are as expected.
        """
        url = 'test_url'
        expected = dict(url=url, data='data')
        parser.parse_feed.return_value.to_json.return_value = json.dumps(expected)
        with self.app.test_client() as client:
            res = client.post('/feed/read', json={'url': url})
        reader.get_content.assert_called_with(url)
        reader.get_feed_root.assert_called_with(reader.get_content.return_value)
        parser.parse_feed.assert_called_with(reader.get_feed_root.return_value)
        assert res.status_code == 200
        assert res.get_json() == expected

    @patch('src.feed.blueprint.FeedReader')
    @patch('src.feed.blueprint.FeedParser')
    def test_read_feed_no_url(self, parser, reader):
        """
        We should test whether a BadRequest is being returned in case a url is not provided.
        """
        url = 'test_url'
        with self.app.test_client() as client:
            res = client.post('/feed/read', json={'nourl': url})
        reader.get_content.assert_not_called()
        reader.get_feed_root.assert_not_called()
        parser.parse_feed.assert_not_called()
        assert res.status_code == 400

    @patch('src.feed.blueprint.FeedReader')
    @patch('src.feed.blueprint.FeedParser')
    def test_read_feed_unretrievable_url(self, parser, reader):
        """
        We should test whether a BadRequest is being returned when the provided url cannot be retrieved.
        """
        def exception_side_effect(x):
            raise RequestException()

        url = 'test_url'
        reader.get_content.side_effect = exception_side_effect
        with self.app.test_client() as client:
            res = client.post('/feed/read', json={'url': url})
        reader.get_content.assert_called_with(url)
        reader.get_feed_root.assert_not_called()
        parser.parse_feed.assert_not_called()
        assert res.status_code == 400

    @patch('src.feed.blueprint.FeedReader')
    @patch('src.feed.blueprint.FeedParser')
    def test_read_feed_unparseable_content(self, parser, reader):
        """
        We should test whether a BadRequest is being returned when the provided url's contents cannot be parsed.
        """
        def exception_side_effect(x):
            raise ParseError()

        url = 'test_url'
        reader.get_feed_root.side_effect = exception_side_effect
        with self.app.test_client() as client:
            res = client.post('/feed/read', json={'url': url})
        reader.get_content.assert_called_with(url)
        reader.get_feed_root.assert_called_with(reader.get_content.return_value)
        parser.parse_feed.assert_not_called()
        assert res.status_code == 400
