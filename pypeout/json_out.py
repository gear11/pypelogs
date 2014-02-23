import json
import sys
class JSONOut(object):
    def process(self, pin):
        for e in pin:
            sys.stdout.write(json.dumps(e))
            sys.stdout.write("\n")
            sys.stdout.flush()