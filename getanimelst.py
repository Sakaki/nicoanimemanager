# /usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2, json
from bs4 import BeautifulSoup
from convunichrs import convert

def getAnimelst():
    weekdays = {
        "playerNav3" : "mon",
        "playerNav4" : "tue",
        "playerNav5" : "wed",
        "playerNav6" : "thu",
        "playerNav7" : "fri",
        "playerNav8" : "sat",
        "playerNav9" : "sun"
    }
        
    html = urllib2.urlopen("http://ch.nicovideo.jp/portal/anime?cc_referrer=nicotop_sidemenu")
    soup = BeautifulSoup(html)

    navs = soup.find_all("div", class_="playerNav ")
    navs = filter(lambda item: item["id"] in weekdays.keys(), navs)
    
    animes = []
    for nav in navs:
        items = nav.find_all("li", class_="video cfix ")
        for item in items:
            title = item.find("input", attrs={"name" : "title"})["value"]
            channel = item.find("input", attrs={"name" : "channel_id"})["value"]
            link = "http://ch.nicovideo.jp/" + channel
            weekday = weekdays[nav["id"]]

            print weekday, channel, link, title
            animes.append({"title" : title, "channel" : channel, "link" : link, "weekday" : weekday})

    jsondata = {"allanimes" : animes}
        
    with open("animelst.json", "w") as f:
        f.write(json.dumps(jsondata, "utf-8"))

if __name__ == "__main__":
    getAnimelst()
