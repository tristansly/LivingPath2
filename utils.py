import sys, os
import importlib


def path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def next_key(dict, key):
    keyList = sorted(dict.keys(), key=len )
    for i,v in enumerate(keyList):
        if v == key:
            return keyList[ (i+1) % len(keyList) ]

def prev_key(dict, key):
    keyList = sorted(dict.keys(), key=len )
    for i,v in enumerate(keyList):
        if v == key:
            return keyList[ (i-1) % len(keyList) ]
def next_item(list, glyph):
    for i in range(len(list)) :
        if list[i] == glyph :
            return list[i+1 % len(list)]
def prev_item(list, glyph):
    for i in range(len(list)) :
        if list[i] == glyph :
            return list[i-1 % len(list)]



class Singleton(type):
    def __init__(self, name, bases, mmbs):
        super(Singleton, self).__init__(name, bases, mmbs)
        self._instance = super(Singleton, self).__call__()

    def __call__(self, *args, **kw):
        return self._instance





# class Base_plugin():
#
#     def __init__(self, arg):
#         super(plugin, self).__init__()
#         self.arg = arg
