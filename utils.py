import sys, os
import importlib
import ctypes
import contextlib
import freetype as ft


def load_plugins():
    plugins, names = [], []
    # alternative to importlib :
    from plugins import particles
    from plugins import blur
    from plugins import dilate_erode
    from plugins import pixel
    from plugins import reaction_diffusion
    for i in sys.modules.keys() :
        if i.startswith("plugins.") :
            plugins.append( eval(i.split('.')[1]) )
            names.append( i.split('.')[1] )
    # for i in os.listdir( path("plugins") ):
    #     if not i.startswith("__") and i.endswith(".py") :
    #         name = i.split('.')[0]
    #         print("LOADED PLUGIN : " + name)
    #         plugins.append( importlib.import_module("plugins." + name) )
    #         names.append( name )
    return plugins, names
############## DATA ######################################################
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

            ############## MATHS ######################################################

def mapping(x,a,b,A,B):
    return  ((x-a)/(b-a)) * (B-A) + A

def mapping(x,A,B): # si 0<x<1
    return  x * (B-A) + A


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def ellipse(size,x,y, fill, draw):
    s = int(size/2)
    draw.ellipse((x-s,y-s,x+s,y+s), fill )
def rectangle(size,x,y, fill, draw):
    s = int(size/2)
    draw.rectangle((x-s,y-s,x+s,y+s), fill )

    ############## DRAW PIL ######################################################

def ellipse(size,x,y, fill, draw):
    s = int(size/2)
    draw.ellipse((x-s,y-s,x+s,y+s), fill )
def rectangle(size,x,y, fill, draw):
    s = int(size/2)
    draw.rectangle((x-s,y-s,x+s,y+s), fill )

    ############## fontTools outlines ######################################################

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
