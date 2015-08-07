# /usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2, sys
from xml.etree.ElementTree import fromstring

def getVideoInfo(vid):
    url = "http://ext.nicovideo.jp/api/getthumbinfo/"+vid
    res = urllib2.urlopen(url)
    xmlbody = res.read()

    elem = fromstring(xmlbody)
    date = elem.findtext(".//first_retrieve")

    result = {
        "date" : date
    }

    return result

if __name__ == "__main__":
    print getVideoInfo(sys.argv[1])
