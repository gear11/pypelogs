import g11pyutils as utils
import logging
LOG = logging.getLogger("csv_in")

DELIM = ','
class CSVIn(object):
    def __init__(self, spec=None):
        args = spec.split(",", 1)
        if len(args) > 1:
            self.opts = utils.to_dict(args[1])
        else:
            self.opts = {}
        self.headers = None
        self.fo = utils.fopen(args[0], self.opts.get('enc', 'utf-8'))

    @staticmethod
    def unquote(s):
        if len(s) < 2:
            return s
        c = s[0]
        if c == '"' or c == "'" and c == s[-1]:
            return s[1:-1]
        else:
            return s

    def __iter__(self):
        count = 0
        for line in self.fo:
            count += 1
            if not self.headers:
                self.headers = [CSVIn.unquote(s) for s in line.strip().split(DELIM)]
                continue
            try:
                e = {}
                vals = [CSVIn.unquote(s) for s in line.strip().split(DELIM)]
                i = 0
                for h in self.headers:
                    e[h] = vals[i]
                    i += 1
                yield e
            except Exception, ex:
                LOG.warn("Exception parsing input line %s: %s", count, ex)