# /usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, request, send_from_directory, redirect
import json, os, socket, os
import api

app = Flask(__name__)

@app.route('/')
def index():
    return redirect("/webui/index.html")

@app.route('/webui/<path:path>')
def server_static(path):
    htmldir = os.path.abspath(os.path.dirname(__file__)) + "/html"
    return send_from_directory(htmldir, path)

@app.route('/api/<command>', methods=["POST", "GET"])
def postApi(command):
    print "API : ", command

    params = {}
    for k, v in request.args.items():
        params[k.encode("utf-8")] = v.encode("utf-8")
    
    method = getattr(api, command)
    retcode, ret = method(params)

    return json.dumps(ret, "utf-8")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000, threaded=True)
