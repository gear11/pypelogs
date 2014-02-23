from wikip import WikipArticles, WikipGeo
from text import Text
from json_in import JSON
CLASSES = {
    'text' : Text,
    'json' : JSON,
    'wikip' : WikipArticles,
    'wikig' : WikipGeo
}

def input_for(s):
    spec_args = s.split(':', 1)
    clz = CLASSES.get(spec_args[0])
    if not clz:
        raise ValueError("No such input type: %s", spec_args[0])
    return clz() if len(spec_args) == 1 else clz(spec_args[1])