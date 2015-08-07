# /usr/bin/env python
# -*- coding:utf-8 -*-

from bottle import Bottle, run, request, static_file
from multiprocessing import Process
import json, os
import api

app = Bottle()

@app.route('/webui/<filepath:path>')
def server_static(filepath):
    htmldir = os.path.abspath(os.path.dirname(__file__)) + "/html"
    return static_file(filepath, root=htmldir)

@app.route('/api/<command>', method="GET")
@app.route('/api/<command>', method="POST")
def postApi(command=None):
    print "API : ", command

    method = getattr(api, command)
    retcode, ret = method(request.params)

    return json.dumps(ret, "utf-8").decode()


#if __name__ == "__main__":
#    run(app, host='localhost', port=8080)


def main():
    t = Process(target=run(app, host='localhost', port=8080))    
    try:
        t.daemon = True
        t.start()
        t.join()
    
    except KeyboardInterrupt:
        sys.stdout.write("Aborted by user.\n")
        sys.exit(1)

    except Exception as e:
        t.terminate()
        main()

if __name__ == "__main__":
    main()
