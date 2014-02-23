from head import Head
from each import Each

CLASSES = {
    'each' : Each,
    'head' : Head
}

def filter_for(s):
    spec_args = s.split(':', 1)
    clz = CLASSES.get(spec_args[0])
    if not clz:
        raise ValueError("No such filter type: %s", spec_args[0])
    return clz() if len(spec_args) == 1 else clz(spec_args[1])
