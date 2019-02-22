import json


class Feed:
    """
    Class representing a parsed Feed.

    We collect nothing but the item list from the original feed.
    """

    def __init__(self, items=list()):
        self.items = items

    def to_dict(self):
        """
        Dictionary representation of the feed

        :return: Dictionary representation of the feed.
        """
        return dict(feed=[item.to_dict() for item in self.items])

    def to_json(self):
        """
        JSON-like representation of the feed. It differs from a common JSON in the sense that the list of items
        actually contains dict-like pairs, with an "item" key referencing each item's contents.

        :return: JSON-like representation of the feed.
        """
        return '{"feed": [' + ','.join([f'"item": {json.dumps(item.to_dict(), ensure_ascii=False)}'
                                        for item in self.items]) + ']}'


class FeedItem:
    """
    Class representing a parsed Feed Item, containing it's title, link and description.
    """

    def __init__(self, title=None, link=None, description=None):
        self.title = title
        self.link = link
        self.description = description

    def to_dict(self):
        """
        Dictionary representation of the feed item.

        :return: Dictionary representation of the feed item.
        """
        return dict(title=self.title,
                    link=self.link,
                    description=[block.to_dict() for block in self.description])


class FeedItemDescriptionBlock:
    """
    Class representing a Feed Item's Description Block. It can have one of three content types: text, image or links.

    - Text blocks contain it's simple text content;
    - Image blocks contain the image url;
    - Links blocks contain a list of urls.
    """

    TEXT_TYPE = 'text'
    IMAGE_TYPE = 'image'
    LINKS_TYPE = 'links'

    def __init__(self, type=None, content=None):
        self.type = type
        self.content = content

    def to_dict(self):
        """
        Dictionary representation of the description block.

        :return: Dictionary representation of the description block.
        """
        return dict(type=self.type, content=self.content)
