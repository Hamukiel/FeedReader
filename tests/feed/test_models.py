import unittest
from unittest.mock import MagicMock

from src.feed.models import Feed, FeedItem, FeedItemDescriptionBlock


class ModelTests(unittest.TestCase):
    """
    TestCase including tests for the feed model classes
    """

    def test_feed_creation(self):
        """
        Test whether the Feed object is being correctly created.
        """
        items = []
        feed = Feed(items)
        assert isinstance(feed, Feed)
        assert items == feed.items

    def test_empty_feed_to_dict(self):
        """
        Testing if an empty Feed's to_dict behaves as expected.
        """
        expected = dict(feed=[])
        feed = Feed()
        assert feed.to_dict() == expected

    def test_feed_to_dict(self):
        """
        Making sure that Feed.to_dict() correctly produces a valid dictionary based on its items' values
        """
        item = MagicMock()
        items = [item]
        feed = Feed(items)
        res = feed.to_dict()
        item.to_dict.assert_called()
        expected = dict(feed=[item.to_dict()])
        assert res == expected

    def test_empty_feed_to_json(self):
        """
        Although the to_json function is pretty similar to the to_dict, we should also make sure that its behavior
        ir correct in case of an empty feed.
        """
        expected = '{"feed": []}'
        feed = Feed()
        assert feed.to_json() == expected

    def test_feed_to_json(self):
        """
        We should make sure that the to_json function generates a JSON-like structure correctly, with its "items" keys
        """
        expected = '{"feed": ["item": {"a": "a", "b": "b", "c": []}]}'
        item = MagicMock()
        item.to_dict.return_value = dict(a='a', b='b', c=[])
        items = [item]
        feed = Feed(items)
        res = feed.to_json()
        item.to_dict.assert_called()
        assert res == expected

    def test_feed_item_creation(self):
        """
        Test whether the FeedItem object is being correctly created.
        """
        title = 'title'
        link = 'link'
        description = 'description'
        item = FeedItem(title, link, description)
        assert isinstance(item, FeedItem)
        assert item.title == title
        assert item.link == link
        assert item.description == description

    def test_feed_item_to_dict(self):
        """
        Making sure that the FeedItem's to_dict function correctly generates a dictionary based on its values.
        """
        title = 'title'
        link = 'link'
        block = MagicMock()
        description = [block]
        item = FeedItem(title, link, description)
        res = item.to_dict()
        block.to_dict.assert_called()
        expected = dict(title=title, link=link, description=[block.to_dict.return_value])
        assert res == expected

    def test_feed_block_creation(self):
        """
        Test whether the FeedItemDescriptionBlock object is being correctly created.
        """
        content_type = 'text'
        content = 'content'
        block = FeedItemDescriptionBlock(content_type, content)
        assert isinstance(block, FeedItemDescriptionBlock)
        assert block.type == content_type
        assert block.content == content

    def test_feed_block_to_dict(self):
        """
        Making sure that the FeedItemDescriptionBlock's to_dict function correctly generates a dictionary based on
        its values.
        """
        content_type = 'text'
        content = 'content'
        expected = dict(type=content_type, content=content)
        block = FeedItemDescriptionBlock(content_type, content)
        assert block.to_dict() == expected
