import g11pyutils as utils
import xml.etree.ElementTree as ET
import logging
import re

LOG = logging.getLogger("wikip")


class WikipArticles(object):
    """Iterates over a Wikipedia XML article dump, producing one event per article.

    The event is a deeply-nested dict matching the article XML and capturing the full article contents.
    """
    def __init__(self, article_file=None, filter = None):
        self.fo = utils.fopen(article_file)
        self.filter = filter
        LOG.info("Using ElementTree version %s", ET.VERSION)

    def __iter__(self):
        # get an iterable
        context = ET.iterparse(self.fo, events=("start", "end"))
        ET.register_namespace('', 'http://www.mediawiki.org/xml/export-0.8/')
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        LOG.info("Root attrib: %s", root.attrib)
        for event, el in context:
            tag = bare(el.tag)
            LOG.debug("Event: %s, El: %s, Tag: '%s'", event, el, tag)
            if event == "end" and tag == "page":
                d = utils.etree_to_dict(el)
                if self.filter:
                    try:
                        d = self.filter(d)
                        if d:
                            yield d
                    except Exception, e:
                        LOG.warn("Exception filtering article: %s", e)
                else:
                    yield d
            root.clear() # clear each time to prevent memory growth

class WikipGeo(WikipArticles):
    def __init__(self, article_file=None):
        super(WikipGeo, self).__init__(article_file, geo_filter)

def wikip_url(s):
    return 'http://wikipedia.org/wiki/'+s.replace(' ', '_')

def geo_filter(d):
    """Inspects the given Wikipedia article dict for geo-coordinates.

    If no coordinates are found, returns None.  Otherwise, returns a new dict
    with the title and URL of the original article, along with coordinates."""
    page = d["page"]
    if not page.has_key("revision"):
        return
    title = page["title"]
    text = page["revision"]["text"]
    if not utils.is_str_type(text):
        if text.has_key("#text"):
            text = text["#text"]
        else:
            return
    LOG.debug("--------------------------------------------------------------")
    LOG.debug(title)
    LOG.debug("--------------------------------------------------------------")
    LOG.debug(text)
    c = find_geo_coords(text)
    return { "source" : "wikipedia", "title" : title, "url" : wikip_url(title), "coords" : c } if c else None


def bare(tag):
    """Returns a tag stripped of preceding namespace info"""
    n = tag.rfind('}')
    return tag[n+1:] if n >= 0 else tag

'''
| latitude = 48.8738
| longitude = 2.2950
'''
INFO_BOX_LAT_LON = re.compile(r"\|\s*latitude\s*=\s*(-?[\d\.]+)\s*\|\s*longitude\s*=\s*(-?[\d\.]+)", re.MULTILINE | re.UNICODE )
'''
{{coord|35.0797|-80.7742|region:US-NC_type:edu|display=title}}
{{coord|77|51|S|166|40|E|}}
'''
COORDS_LAT_LON_DEG_MIN = re.compile(r"\{\{coord\|(\d+)\|(\d+)\|([NS])\|(\d+)\|(\d+)\|([EW])\|", re.MULTILINE | re.UNICODE )
COORDS_LAT_LON_DEC = re.compile(r"\{\{coord\|(-?\d+\.\d+)\|(-?\d+\.\d+)\|", re.MULTILINE | re.UNICODE )

def find_geo_coords(s):
    """Returns a list of lat/lons found by scanning the given text"""
    coords = []
    LOG.debug("Matching in text size %s", len(s))
    for m in re.findall(COORDS_LAT_LON_DEG_MIN, s):
        LOG.debug("Matched: %s", m)
        lat = (float(m[0]) + float(m[1])/60.0) * (1 if m[2].upper() == 'N' else -1)
        lon = (float(m[3]) + float(m[4])/60.0) * (1 if m[5].upper()  == 'E' else -1)
        coords.append((lat, lon))
    coords.extend([(float(m[0]), float(m[1])) for m in re.findall(INFO_BOX_LAT_LON, s)])
    coords.extend([(float(m[0]), float(m[1])) for m in re.findall(COORDS_LAT_LON_DEC, s)])
    l = []
    for c in set(coords): # Dedupe; the reality is non-trivial though...
        if (c[0] > 90 or c[0] < -90 or c[1] > 180 or c[1] < -180):
            LOG.warn("Invalid coords: %s", c)
        else:
            l.append({ "type": "Point", "coordinates": (c[1], c[0]) }) # GeoJSON, lon goes first
    return l