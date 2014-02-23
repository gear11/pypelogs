import g11pyutils as utils
import pymongo
import logging
import pprint

LOG = logging.getLogger("MongoDB")

class MongoDB(object):
    def __init__(self, spec, host='127.0.0.1', port=27017, buffer=1000):
        LOG.warn(pymongo.get_version_string())
        args = spec.split(",", 1)
        self.db, self.coll = args[0].split(".")
        opts = utils.to_dict(args[1]) if len(args) > 1 else {}
        self.host = opts.get("host", host)
        self.port = opts.get("port", port)
        self.buffer = opts.get("b", buffer)
        self.id = opts.get("id")
        def do_connect():
            return self.do_connect()
        def do_close():
            return self.do_close()
        self.conn = utils.Connector(do_connect, do_close)
        self.conn.connect()

    def do_connect(self):
        mongo_client = pymongo.MongoClient(self.host, self.port)
        if not self.db in mongo_client.database_names():
            raise ValueError("No database named '%s'", self.db)
        db = mongo_client[self.db]
        if not self.coll in db.collection_names():
            raise ValueError("Database '%s' has no collection named '%s'" % (self.db, self.coll))
        return mongo_client

    def collection(self):
        mongo_client = self.conn.c()
        if not mongo_client:
            raise Exception("Not connected")
        if not self.db in mongo_client.database_names():
            raise ValueError("No database named '%s'", self.db)
        db = mongo_client[self.db]
        if not self.coll in db.collection_names():
            raise ValueError("Database '%s' has no collection named '%s'" % (self.db, self.coll))
        return db[self.coll]

    def do_close(self, conn):
        conn.close()

    def send(self, docs):
        LOG.info("Inserting %s docs", len(docs))
        c = self.collection()
        while True:
            try:
                #bulk = c.initialize_unordered_bulk_op()
                #bulk.insert(docs)
                #bulk.execute()
                c.insert(docs, manipulate=False, continue_on_error=True)
                break
            except pymongo.errors.DuplicateKeyError as dke:
                pprint.pprint(dke)
                break
            except Exception as ex:
                LOG.warn("Bulk insert failed: %s", ex)
                if self.is_connect_err(ex):
                    self.conn.reconnect()
                else:
                    break

    def is_connect_err(self, ex):
        if repr(ex).find('E11000') >= 0:
            return False
        return True

    def process(self, pin):
        buff = []
        for e in pin:
            if self.id: # Set ID if an ID field was specified
                e['_id'] = e[self.id]
            LOG.debug("Inserting %s", e)
            buff.append(e)
            if len(buff) >= self.buffer:
                self.send(buff)
                buff = []
        self.send(buff)