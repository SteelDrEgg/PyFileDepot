'''
This works only on unix-like system
You might need modifications to make it working on windows
'''

import os
from collections import defaultdict
# import json
import re
import fnmatch, glob
import logging

logger = logging.getLogger("mainLogger")


class mappingTable:
    root: dict
    _temp: dict

    '''
    Root structure:
    The end of each branch is real/physical position of the file
    
    root
    |-sub1
    |   |-real position
    |
    |-sub2
        |-ssub1
        |   |-real position
        |
        |-ssub2
            |-real position
    '''

    # _holderPattern: str = r"(.*?)%([^%]*)%([^%]*)$"

    def __init__(self, path: str):
        '''
        :param path: path of the config file
        '''
        file = open(path, "r")
        self.root = self._tree()
        while line := file.readline():
            line = line.replace(os.linesep, "")
            if "://" in line:
                proto, content = line.split("://")
                physical, virtual = content.split(":")
                physical = proto + "://" + physical
            else:
                physical, virtual = line.split(":")
            virtual = virtual.split("/")
            temp = self._put(virtual[1:] + [physical])
            self.root = self._merge(temp, self.root)

    def _tree(self):
        # Credit to https://gist.github.com/hrldcpr/2012250
        return defaultdict(self._tree)

    def _put(self, sets):
        if len(sets) > 1:
            t = self._tree()
            t[sets[0]] = self._put(sets[1:])
            return dict(t)
        else:
            t = self._tree()
            t[str(sets[0])]
            return dict(t)

    def _merge(self, a: dict, b: dict, path=[]):
        # Credit to https://stackoverflow.com/a/7205107
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self._merge(a[key], b[key], path + [str(key)])
                elif a[key] != b[key]:
                    raise Exception('Conflict at ' + '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    def getPositionFromPath(self, path):
        '''
        Use a set of rules to find the node from the tree
        :param path: url accessed
        :return: ( matched node from file tree :dict ), ( args in url which inside %% :dict )
        '''
        path = path.split("/")
        temp = self.root
        args = {}
        for pt in path:
            for ele in temp:
                if "%" in ele:
                    # Match everything in %%
                    placeHolders = re.findall(r'%(.*?)%', ele)
                    if not placeHolders:
                        logger.error("config error at " + ele)
                    # Replace %% with * and do regex
                    compiledPattern = re.sub(r'%(.*?)%', r'(.*?)', ele)
                    if compiledPattern != r"(.*?)":  # If it's like this: "%arg%"
                        matches = re.match(compiledPattern, pt)
                        if not matches:
                            continue
                        extracted = matches.groups()
                    else:
                        extracted = [pt]
                    if extracted:
                        args.update(dict(zip(placeHolders, extracted)))
                        temp = temp[ele]
                        break
                elif "*" in ele or "?" in ele:
                    if fnmatch.fnmatchcase(pt, ele):
                        temp = temp[ele]
                        break
                else:
                    if ele == pt:
                        temp = temp[ele]
                        break

        if temp == self.root:
            return False, None
        return temp, args


def fileOrFolder2ListOfAddr(obj: dict):
    '''

    :param obj: first return value from mappingTable.getPositionFromPath
    :return: If File, return (real position):str ; If Folder, return (file names):list
    '''
    for key in obj:
        if len(obj[key]) != 0:
            return list(obj)
    return list(obj)[0]


def addArgs2position(position, args):
    '''
    Fill template with args
    :param position: template with %arg%
    :param args: dict of args {name:value}
    :return: physical location on machine
    '''
    def replace(match):
        return str(args.get(match.group(1), match.group(0).replace("%", "")))

    return re.sub(r'%(\S+)%', replace, position)


def selectLocalFiles(template: str, args: dict = None):
    '''
    Turn virtual path into real local path
    :param template: template with %arg% or * or plain location
    :param args: dict of args {name:value}
    :return: physical location on machine
    '''
    if args:
        path = addArgs2position(template, args)
        if os.path.exists(path):
            if os.path.isdir(path):
                return os.listdir(path)
            else:
                return path
        else:
            logger.error(f"Invalid path '{template}' configured")
    elif "*" in template or "?" in template:
        return glob.glob(template)
    else:
        return template
