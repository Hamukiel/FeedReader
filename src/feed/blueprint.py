from xml.etree.ElementTree import ParseError

from flask import Blueprint, request, make_response
from requests import RequestException
from werkzeug.exceptions import BadRequest

from src.feed.reader import FeedReader, FeedParser


def create_blueprint():
    bp = Blueprint('feed', __name__, url_prefix='/feed')
    return bp


mod_feed = create_blueprint()


@mod_feed.route('/read', methods=['POST'])
def read_feed():
    jdata = request.get_json()
    try:
        url = jdata['url']
    except KeyError:
        raise BadRequest('Request missing url')

    try:
        content = FeedReader.get_content(url)
    except RequestException:
        raise BadRequest("The url could not be requested")

    try:
        root = FeedReader.get_feed_root(content)
    except ParseError:
        raise BadRequest("The requested url's contents could not be parsed")

    feed = FeedParser.parse_feed(root)
    response = make_response(feed.to_json())
    response.mimetype = 'application/json'
    return response, 200
