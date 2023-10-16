import configparser
import logging


class config:
    ip: str
    port: int
    static_folder: str = None
    template_folder: str = None

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("../PyFileDepot.ini")

        try:
            self.ip = config["server"]["ip"]
            self.port = int(config["server"]["port"])
        except KeyError as e:
            

        # try:
        #     if "static_folder" in config["style"].keys():
        #         self.static_folder = config["style"]["static_folder"]
        #     if "template_folder" in config["style"].keys():
        #         self.template_folder = config["style"]["template_folder"]


a = config()
