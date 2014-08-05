import g11pyutils as utils
import logging
import json

LOG = logging.getLogger("Flickr")


class Flickr(object):
    """
    Input from the Flickr API
    """
    def __init__(self, spec):
        args = spec.split(',')
        creds_fname = args[0]
        if len(args) > 1:
            self.cmds = args[1:]
        else:
            self.cmds = ['interesting']
        # Parse creds file
        with utils.fopen(creds_fname) as fo:
            creds = dict((k, v) for k, v in [l.strip().split('=', 1) for l in fo])
        LOG.info("Using creds: %s" % creds)
        # Defer import until we need it
        import flickrapi
        self.flickr = flickrapi.FlickrAPI(creds['api_key'], creds['api_secret'], format='json')

    def __iter__(self):
        for cmd in self.cmds:
            n = cmd.find('=')  # Arguments, as in interesting=owner_name,date_upload
            if n > 0:
                args = cmd[n+1:].split(',')
                cmd = cmd[0:n]
            else:
                args = None
            try:
                yielded = 0
                rsp = getattr(self, cmd)(args)
                for e in rsp:
                    yielded += 1
                    yield e
                LOG.info("Method '%s' yielded %s rows" % (cmd, yielded))
            except Exception, err:
                LOG.error("Error-Message: %s", err.message)

    def interesting(self, args=None):
        extras = ','.join(args) if args else 'last_update,geo,owner_name,url_sq'
        page = 1
        while True:
            LOG.info("Fetching page %s" % page)
            rsp = self.load_rsp(self.flickr.interestingness_getList(extras=extras, page=page))
            #LOG.info("Flickr response: (%s) %s" % (type(rsp), rsp))
            if rsp["stat"] == "ok":
                photos = rsp["photos"]
                if int(photos["page"]) < page:
                    LOG.info("End of Flickr pages (%s pages with %s per page)" % (photos["pages"], photos["perpage"]))
                    break
                for p in photos["photo"]:
                    yield p
                page += 1
            else:
                yield [rsp]
                break

    @staticmethod
    def load_rsp(rsp):
        first = rsp.find('(') + 1
        last = rsp.rfind(')')
        return json.loads(rsp[first:last])
