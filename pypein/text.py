import g11pyutils as utils
import xml.etree.ElementTree as ET
import logging
"""
Contains classes for dealing with Wikipedia input.
"""
LOG = logging.getLogger("wikip")


class WikipArticles(object):
    def __init__(self, article_file, filter = None):
        self.fo = utils.fopen(article_file)

    def __iter__(self):
        # get an iterable
        context = ET.iterparse(self.fo, events=("start", "end"))
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        for event, el in context:
            if event == "end" and el.tag == "page":
                if el.attrib.has_key("tag"):
                    LOG.warn("Overwriting tag attribute of %s %s", el.tag, el.attrib)
                el.attrib["tag"] = el.tag # Assign the tagname to the attributes dict
                yield el.attrib
            root.clear()

