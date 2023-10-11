import sys, os
import importlib
import ctypes
import contextlib
import freetype as ft

def load_plugins():
    plugins, names = [], []
    for i in os.listdir("./plugins"):
        if not i.startswith("__") and i.endswith(".py") :
            name = i.split('.')[0]
            print("LOADED PLUGIN : " + name)
            plugins.append( importlib.import_module("plugins." + name))
            names.append( name )
            if "outline" in i :
                names.insert(0, names.pop( len(names)-1 ) )
                plugins.insert(0, plugins.pop( len(plugins)-1 ) )
    return plugins, names

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



@contextlib.contextmanager
def new_outline(n_points, n_contours):
    library = ft.get_handle()
    raw_ft_outline = ft.FT_Outline()
    err = ft.FT_Outline_New( library, ft.FT_UInt(n_points), ft.FT_Int(n_contours), ctypes.byref(raw_ft_outline) )
    if err: raise ft.FT_Exception(err)
    try:
        raw_ft_outline.n_points   = 0
        raw_ft_outline.n_contours = 0
        yield ft.Outline(raw_ft_outline)
    finally:
        ft.FT_Outline_Done(library, ctypes.byref(raw_ft_outline))
