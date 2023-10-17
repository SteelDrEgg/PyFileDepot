import os


class fileMap:
    name: str
    position: str

    def __int__(self, name, position):
        self.name = name
        self.position = position


class folder:
    name: str
    children: dict

    def __int__(self, name):
        self.name = name


class mappingTable:
    root: folder

    def __init__(self, path: str):
        file = open(path, "r")
        while line := file.readline():
            line = line.replace(os.linesep, "")
            line = line.split(os.sep)


a = mappingTable("../config.conf")
