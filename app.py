import flask
from flask import Flask
from flask import render_template, jsonify

from util import initConfig

config = initConfig()

app = Flask(__name__, static_folder=config.static_folder, template_folder=config.template_folder)

@app.route('/')
def root():
    # 将捕获到的路径参数传递给视图函数
    return 'root'


@app.route('/<path:path>')
def catch_all(path):

    return 'Catchall route: %s' % path


if __name__ == '__main__':
    app.run(host=config.ip, port=config.port, debug=True)
