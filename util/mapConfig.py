'''
This works only on unix-like system
You might need modifications to make it working on windows
'''

import os
from collections import defaultdict
import json
import re
import fnmatch
import logging

logger = logging.getLogger("mainLogger")


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
    root: dict
    _temp: dict

    # _holderPattern: str = r"(.*?)%([^%]*)%([^%]*)$"

    def __init__(self, path: str):
        file = open(path, "r")
        self.root = self._tree()
        while line := file.readline():
            line = line.replace(os.linesep, "")
            physical, virtual = line.split(":")
            virtual = virtual.split("/")
            # for pt in (virtual[1:] + [physical]):
            #     if pt not in dict(self.root).keys():
            temp = self._put(virtual[1:] + [physical])
            self.root = self._merge(temp, self.root)
        # print(json.dumps(self._tree2dict(self.root), indent=4))

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

    def _tree2dict(self, t):
        # Credit to https://gist.github.com/hrldcpr/2012250
        return {k: self._tree2dict(t[k]) for k in t}

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

    def getValFromPath(self, path):
        path = path.split("/")
        temp = self.root
        args = {}
        for pt in path:
            for ele in temp:
                if "%" in ele:
                    # Match everything in %%
                    placeHolders = re.findall(r'%(.*?)%', ele)
                    print(ele)
                    if not placeHolders:
                        logger.error("config error at " + ele)
                    # Replace %% with * and do regex
                    compiledPattern = re.sub(r'%(.*?)%', r'(.*?)', ele)
                    if compiledPattern != r"(.*?)": # If it's like this: "%arg%"
                        matches = re.match(compiledPattern, pt)
                        if not matches:
                            continue
                        extracted_values = matches.groups()
                    else:
                        extracted_values = [pt]
                    if extracted_values:
                        args.update(dict(zip(placeHolders, extracted_values)))
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
        possibles = list(temp.keys())
        if len(possibles) == 1:
            return possibles[0], args
        else:
            return False, args
