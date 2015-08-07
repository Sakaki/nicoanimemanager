# /usr/bin/env python
# -*- coding:utf-8 -*-

import json, os, shutil, time
from multiprocessing import Process
import config, getchannelinfo, downloadflv
from getanimelst import getAnimelst

dlproc = None
dlallproc = None

dlinfo = {
    "title": "",
    "vname": "",
}

def addrec(params):
    channel = params["channel"]
    config.addRecording(channel)

    return True, None

def getallrecs(params):
    conf = config.readConf()
    return True, {"result" : conf["recording"]}

def delrec(params):
    channel = params["channel"]
    config.removeRecording(channel)

    return True, None

def getanimelst(params):
    with open("animelst.json", "r") as f:
        data = json.loads(f.read(), "utf-8")

    return True, data

def downloadvideo(params, api=True):
    global dlproc
    global dlinfo

    if dlproc != None and dlproc.is_alive() == True:
        result = {"result" : 1}
    else:
        title = params["title"]
        vname = params["vname"]
        vid = params["vid"]

        conf = config.readConf()
        mail = conf["mail"]
        passwd = conf["passwd"]

        args = [
            '-u', mail, '-p', passwd,
            '-l', 'html/video/'+title,
            '-n', vname+'.flv',
            vid
        ]

        dlinfo["title"] = title
        dlinfo["vname"] = vname

        dl = downloadflv.DownloadFlv(args)
        dlproc = Process(target=dl.invoke)
        dlproc.start()

        result = {"result" : 0}

    return True, result

def dlstate(params, api=True):
    #0: 停止 1: 実行中
    global dlproc
    global dlinfo

    if dlproc != None and dlproc.is_alive():
        return True, {"result" : 1, "title" : dlinfo["title"]}
    else:
        return True, {"result" : 0}

def updatechinfo(params):
    reclst = config.readConf()["recording"]
    for channel in reclst:
        try:
            getchannelinfo.getChannelInfo(channel)
        except Exception as e:
            print "取得失敗", e

    return True, {"result" : "success"}

def getdetail(params, api=True):
    title = params["title"]

    jsonfile = "html/video/" + title + "/info.json"
    if not os.path.exists(jsonfile):
        updatechinfo(None)
        if not os.path.exists(jsonfile):
            return False, None
    
    with open(jsonfile, "r") as f:
        data = json.loads(f.read(), "utf-8")

    if api:
        return True, data
    else:
        return data

def getrecorded(params, api=True):
    path = "html/video/"
    if not os.path.exists(path):
        os.makedirs(path)

    rectitles = os.listdir(path)

    result = {"titles" : []}
    for title in rectitles:
        confpath = path + title + "/info.json"
        if not os.path.exists(confpath):
            continue
        with open(confpath) as f:
            jsondata = json.loads(f.read(), "utf-8")
        channel = jsondata["channel"]
        result["titles"].append({"title" : title, "channel" : channel})

    if api:
        return True, result
    else:
        return result

def getvideostate(params, api=True, masterProc=True):
    # 0: 録画不可 1: 録画可 2: 録画済 3: 録画中
    global dlproc, dlinfo

    title = params["title"]
    vname = params["vname"]

    if masterProc:
        downloading = dlproc != None and dlproc.is_alive()
    else:
        downloading = False

    if downloading and dlinfo["title"] == title and dlinfo["vname"] == vname:
            result = {"result" : 3}
    elif os.path.exists("html/video/"+title+"/"+vname+".flv"):
        result = {"result" : 2}
    else:
        with open("html/video/"+title+"/info.json", "r") as f:
            jsondata = json.loads(f.read(), "utf-8")

        for story in jsondata["stories"]:
            if story["title"] == vname.decode("utf-8"):
                recordable = not story["pay"]
                break

        if recordable:
            result = {"result" : 1}
        else:
            result = {"result" : 0}

    if api:
        return True, result
    else:
        return result

def refreshanimelst(params):
    getAnimelst()
    return True, {"result" : "success"}

def delanime(params):
    title = params["title"]
    channel = params["channel"]

    config.removeRecording(channel)

    path = "html/video/"+title
    if title != "" and os.path.exists(path):
        shutil.rmtree(path)

    return True, {"result" : "success"}

def delstory(params):
    title = params["title"]
    vname = params["vname"]

    path = "html/video/" + title + "/" + vname + ".flv"

    if os.path.exists(path):
        os.remove(path)
    else:
        print "そんなパスはない :" + path

    while os.path.exists(path):
        time.sleep(1)
        
    return True, {"result" : "success"}

def dlallanimes(params):
    global dlallproc

    if dlallproc != None and dlallproc.is_alive() == True:
        result = {"result" : 1}
    else:
        dlallproc = Process(target=_dlall_wrapper, args=(None,))
        dlallproc.start()

        result = {"result" : 0}

    return True, result

def _dlall_wrapper(params):
    for titleinfo in getrecorded(None, api=False)["titles"]:
        title = titleinfo["title"]
        for storyinfo in getdetail({"title" : title}, api=False)["stories"]:
            try:
                vname = storyinfo["title"].encode("utf-8")
                vid = storyinfo["vid"].encode("utf-8")
                if getvideostate({"title" : title, "vname" : vname}, api=False, masterProc=False)["result"] == 1:
                    conf = config.readConf()
                    mail = conf["mail"]
                    passwd = conf["passwd"]
                
                    args = [
                        '-u', mail, '-p', passwd,
                        '-l', 'html/video/'+title,
                        '-n', vname+'.flv',
                        vid
                    ]

                    dlinfo["title"] = title
                    dlinfo["vname"] = vname

                    downloadflv.DownloadFlv(args).invoke()
            except Exception as e:
                print e

    return True, {"result" : "success"}

def readconf(params):
    return True, {"result" : config.readConf()}

def writeconf(params):
    confdata = params["conf"].decode("utf-8")
    print confdata, type(confdata)
    if confdata != "":
        config.writeConf(confdata)

    return True, {"result" : "success"}

def resetconf(params):
    config.reset()

    return True, {"result" : "success"}
