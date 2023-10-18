import configparser
import logging
from util import loggings


class initConfig:
    ip: str
    port: int
    static_folder: str = None
    template_folder: str = None
    map_config: str = "config.conf"

    _config: configparser.ConfigParser

    def __init__(self):
        # Setup config
        self._config = configparser.ConfigParser()
        self._config.read("PyFileDepot.ini")

        # Setup logging
        logLevel = loggings.level.INFO
        if loglevel := self._getValueIfAvailable(["server", "log_level"]):
            logLevel = loggings.level(loglevel)
        if path := self._getValueIfAvailable(["server", "log_file"]):
            loggings.configLoggin(logLevel, path)
            print(path)
        else:
            loggings.configLoggin(logLevel)

        # Parsing config
        self.ip = "0.0.0.0"
        if temp := self._getValueIfAvailable(["server", "ip"]):
            self.ip = temp
        self.port = 5000
        if temp := self._getValueIfAvailable(["server", "port"]):
            self.port = int(temp)
        # Parsing style
        template = "default"
        self.static_folder = "templates/{template}/static"
        self.template_folder = "templates/{template}/html"

        if (temp := self._getValueIfAvailable(["style", "style_folder"])) and temp:
            self.template_folder = temp + "/{template}/static"
            self.static_folder = temp + "/{template}/html"
        if (temp := self._getValueIfAvailable(["style", "static_folder"])) and temp:
            self.static_folder = temp
        if (temp := self._getValueIfAvailable(["style", "html_folder"])) and temp:
            self.template_folder = temp
        if (temp := self._getValueIfAvailable(["style", "template"])) and temp:
            template = temp

        self.static_folder = self.static_folder.format(template=template)
        self.template_folder = self.template_folder.format(template=template)

        if (temp := self._getValueIfAvailable(["server", "file_map_config"])) and temp:
            self.map_config = temp

    def _getValueIfAvailable(self, key, errMsg: str = None):
        try:
            iterKey = iter(key)
            temp = self._config[next(iterKey)]
            for pt in iterKey:
                temp = temp[pt]
            return temp
        except KeyError as e:
            if errMsg:
                logger = logging.getLogger('mainLogger')
                logger.error(errMsg.format(err=e))
            return False
