#!/bin/sh

#
# Fetches interesting Flickr photos to a named directory.
#
# Sample usage: flickr_to_dir.sh ../data/flickr
#
python pypelogs.py --info flickr:../GPSPressServer/data/flickr.creds \
    'exec:e["url"]="https://farm%s.staticflickr.com/%s/%s_%s_b.jpg"%(e["farm"],e["server"],e["id"],e["secret"])' \
    keep:url wget:$1
