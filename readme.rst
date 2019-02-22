FeedReader
==========

FeedReader is a simple API for parsing data from XML Feeds into a JSON-like structure.

It uses Beaultiful Soup 4 for http parsing and the stdlib's etree for XML parsing.

Example request:

.. code-block:: text

   curl -i -X POST \
   -H "Content-Type:application/json" \
   -d \
    '{"url": "https://revistaautoesporte.globo.com/rss/ultimas/feed.xml"}' \
    'http://127.0.0.1:5000/feed/read'

/feed/read
----------

The Feed Read endpoint expects a JSON Request containing a **url** parameter, which is expected to be filled
with a valid feed url. It expects the structure:

.. code-block:: xml

    <rss ...>
        <channel>
            <item>
                <title/>
                <link/>
                <description/>
            </item>
            <item>
                <title/>
                <link/>
                <description/>
            </item>
            <...>
        </channel>
    </rss>



The description tag content is expected to be structured as an HTML with text, image and link tags, each being
parsed as a different type of ContentBlock:

- Paragraph tags (*<p>*) are parsed as text content blocks, with its text content in the **content** tag.
- Image tags (*<img>*) inside divs(*<div>*), are parsed as image content blocks, with its *src* attribute
in the **content** tag
- Links tags ('<ul>') inside divs(*<div>*), are parsed as link content blocks, with the links from its
<il><a href> tags in the **content** tag

The output JSON-like structure will be:

.. code-block:: text

    {
        "feed": [
            "item": {
                "title": "título",
                "link": "link",
                "description": [
                    {
                        "type": "text",
                        "content": "conteudo"
                    },
                    {
                        "type": "image",
                        "content": "url"
                    },
                    {
                        "type": "links",
                        "content": ["url_link_1", "url_link_2", ...]
                    }
                ]
            },
            "item": {
                ...
            }
        ]
    }