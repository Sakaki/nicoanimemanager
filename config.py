# /usr/bin/env python
# -*- coding:utf-8 -*-

import os, json

conffile = "config.json"

def readConf():
    if not os.path.exists(conffile):
        elem = {
            "recording" : [],
            "mail" : "",
            "passwd" : ""
        }
        writeConf(elem)

    with open(conffile, "r") as f:
        conf = f.read()

    return json.loads(conf)

def writeConf(conf):
    jsondata = json.dumps(conf).replace("\\", "")
    if jsondata.startswith('"'):
        jsondata = jsondata[1:]
    if jsondata.endswith('"'):
        jsondata = jsondata[:-1]

    with open(conffile, "w") as f:
        f.write(jsondata)

def addRecording(channel):
    conf = readConf()
    if channel not in conf["recording"]:
        conf["recording"].append(channel)
        writeConf(conf)
    else:
        print "既に登録済みです"

def removeRecording(channel):
    conf = readConf()
    if channel in conf["recording"]:
        conf["recording"].remove(channel)
        writeConf(conf)
    else:
        print "そんな値はない"

def reset():
    os.remove(conffile)
    readConf()
