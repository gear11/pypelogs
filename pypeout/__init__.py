from json_out import JSONOut
from mongodb import MongoDB
CLASSES = {
    'json' : JSONOut,
    'mongodb' : MongoDB
}

def output_for(s):
    spec_args = s.split(':', 1)
    clz = CLASSES.get(spec_args[0])
    if not clz:
        raise ValueError("No such input type: %s", spec_args[0])
    return clz() if len(spec_args) == 1 else clz(spec_args[1])