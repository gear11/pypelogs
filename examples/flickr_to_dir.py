import pypelogs
import sys

specs = [
    'flickr:data/flickr.creds',
    'keep:url',
    'http:'+sys.argv[1]
]

pypelogs.process(specs)
