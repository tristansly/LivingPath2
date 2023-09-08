import utils
from font_utils import *
import gui

from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from tkinterdnd2 import DND_FILES, TkinterDnD
import math
from fontTools import ttLib

import pprint

current_glyph = 'b'
font = ttLib.TTFont(utils.path("files/1.ttf"),lazy=False)
tmp_font = ttLib.TTFont(utils.path("files/1.ttf"))
img = glyph_to_raster(font, current_glyph)

current_plugin = 0

# from time import perf_counter
def get_current_img():
    # print( perf_counter(), " start ")
    img = glyph_to_raster(font, current_glyph)
    # print( perf_counter(), " g to raster ")
    img = algo(img)
    # print( perf_counter(), " algo ")
    path = vectorization( img )
    # print( perf_counter(), " vecto ")
    path_to_font(path, current_glyph, tmp_font)
    # print( perf_counter(), " path to font ")
    img = glyph_to_raster(tmp_font, current_glyph)
    # print( perf_counter(), " g to raster ")
    img = draw_points(path, img)
    # print( perf_counter(), " draw point ")
    return img


def modify_font(out_path):
    print("unprocessed glyphs :")
    for key in font.getGlyphSet():
        # if font["glyf"][glyph].isComposite() : return None # only with simple Glyphs
        if  key in list('qwertyuioplkjhgfdsazxcvbnmV'):
            img = glyph_to_raster(font, key)
            path = vectorization( algo(img) )
            path_to_font(path, key, font)
        else:
            print(key, end=' ')
    font.save(out_path)
    print("Modified font saved successfully!")



import plugins.blur as blur
modules = [blur.Layer()]
names = ['blur']

# def get_plugin(name) :
#     for i in names :
#         if names[0] == name :
#             return modules[0]
#
# # has to be at the end of the file. Idk why ...
# def load_plugins():
#     for i in os.listdir("./plugins"):
#         if not i.startswith("__") and i.endswith(".py") :
#             name = i.split('.')[0]
#             print("LOADED PLUGIN : " + name)
#             modules.append( importlib.import_module("plugins." + name))
#             names.append( name )

def main():

    root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()
    gui.global_Interface(root)
    gui.show_glyph()
    root.mainloop()
    print('main')

    modify_font(utils.path("out.otf"))

def algo(data):
    return modules[0].run(data)


if __name__ == "__main__":
    print('RUN FROM MAIN')
    main()
