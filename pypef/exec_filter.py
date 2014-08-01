import logging
import filter
LOG = logging.getLogger("exec")

class Exec(filter.Filter):
    """Sets specified fields, treating each as a template with the original event subbed in"""
    def __init__(self, spec):
        super(filter.Filter, self).__init__()
        self.expr = compile(spec, '<string>', 'exec')

    def filter_events(self, events):
        for e in events:
            r = 1
            exec(self.expr, {}, {"e": e})
            yield e