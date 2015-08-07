# /usr/bin/env python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import os, sys, urllib2, json
from videoinfo import getVideoInfo

def getChannelInfo(channel):
    html = urllib2.urlopen("http://ch.nicovideo.jp/"+channel+"/video")
    soup = BeautifulSoup(html)

    chname = soup.find("h1", class_="channel_name").text.encode("utf-8")

    chinfo = {"stories" : [], "channel" : channel}
    items = soup.find_all("li", class_="item")
    idx = len(items) - 1
    for item in items:
        pay = False
        for span in item.find("div", class_="item_left").find_all("span"):
            if "all_pay" in span.attrs[u"class"]:
                pay = True

        title = item.h6.a.string
        link = item.a[u"href"]
        vid = link.split("/")[-1]

        chinfo["stories"].append({"title" : title, "link" : link, "vid" : vid, "pay" : pay, "idx" : idx})
        idx -= 1
    
    latestdate = getVideoInfo(vid)["date"]
    chinfo["latest"] = latestdate

    dirname = os.path.abspath(os.path.dirname(__file__)) + "/html/video/" + chname
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        
    with open(dirname+"/info.json", "w") as f:
        f.write(json.dumps(chinfo, "utf-8"))

if __name__ == "__main__":
    getChannelInfo(sys.argv[1])
