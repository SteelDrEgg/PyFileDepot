import flask
from flask import Flask
from flask import render_template, jsonify, redirect, send_file

import util
from util import initConfig, mappingTable

config = initConfig()
mapTable = mappingTable(config.map_config)

app = Flask(__name__, static_folder=config.static_folder, template_folder=config.template_folder)


@app.route('/')
def root():
    page = mapTable.root
    return 'root'


@app.route('/<path:path>')
def catch_all(path):
    infos, args = mapTable.getPositionFromPath(path)
    infos = util.fileOrFolder2ListOfAddr(infos)

    if isinstance(infos, list):
        return "folder " + str(infos) + str(args)
    else:
        return "file " + str(infos) + str(args)
    # position = util.addArgs2position(path, args)
    # if "://" in position:
    #     return redirect(position)
    # else:
    #     return send_file(position)


if __name__ == '__main__':
    app.run(host=config.ip, port=config.port, debug=True)
