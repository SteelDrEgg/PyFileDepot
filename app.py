import flask
from flask import Flask
from flask import render_template, jsonify, redirect, send_file, request
import re, glob, os

import util
from util import initConfig, mappingTable

config = initConfig()
mapTable = mappingTable(config.map_config)

app = Flask(__name__, static_folder=config.static_folder, template_folder=config.template_folder)


@app.route('/')
def root():
    page = mapTable.root
    return 'root'


def not_found(path):
    return render_template("404.html", path="/"+path), 404


@app.route('/<path:path>')
def catch_all(path):
    rawInfos, args = mapTable.getPositionFromPath(path)

    if not rawInfos:
        return not_found(path)

    infos = util.fileOrFolder2ListOfAddr(rawInfos)

    if isinstance(infos, list):
        # Virtual path folder
        # return render_template("index.html", items=infos)
        fileList = []
        for vPath in infos:
            if "%" in vPath:
                realPath = next(iter(rawInfos[vPath]))
                realPath = re.sub(r'%[^%]+%', '*', realPath)
                for file in glob.glob(realPath):
                    if not os.path.isdir(file):
                        file = file.split("/")[-1]
                        # file = file.split("/")[-1]
                        fileList.append({"name": file, "type": "file"})
            elif "*" in vPath:
                realPath = rawInfos[vPath]
                for file in glob.glob(realPath):
                    if not os.path.isdir(file):
                        file = file.split("/")[-1]
                        fileList.append({"name": file, "type": "file"})
            else:
                if len(rawInfos[vPath][next(iter(rawInfos[vPath].keys()))]) == 0:
                    # This is a file, because it has only one child: physical location
                    fileList.append({"name": vPath, "type": "file"})
                else:
                    fileList.append({"name": vPath, "type": "folder"})
        return render_template("index.html", items=fileList, url=request.url)
    else:
        # Real path folder
        location = util.selectLocalFiles(infos, args)
        if location:
            if "://" in location:
                return redirect(location)
            elif isinstance(location, list):
                # Physical folder
                return [i.split("/")[-1] for i in location]
            else:
                return send_file(location)
        else:
            return not_found(path)


if __name__ == '__main__':
    app.run(host=config.ip, port=config.port, debug=True)
# TODO: add support for folder e.g: /folder/:/
