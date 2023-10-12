import utils
from font_utils import *
import gui

from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from tkinterdnd2 import DND_FILES, TkinterDnD
import math, os
from fontTools import ttLib
from functools import partial
import pprint

plugins, names, layers = [], [], []
layer = -1
group = -1
current_glyph = 'b'
root = None
font = ttLib.TTFont(utils.path("files/1.ttf"), recalcBBoxes=False)
tmp_font = ttLib.TTFont(utils.path("files/1.ttf"), recalcBBoxes=False)
img = glyph_to_raster(font, current_glyph)


# from time import perf_counter
def get_current_img():
    # print( perf_counter(), " algo ")
    # print( perf_counter(), " vecto ")
    # print( perf_counter(), " path to font ")
    # print( perf_counter(), " g to raster ")
    # print( perf_counter(), " draw point ")

    img = glyph_to_raster(font, current_glyph)
    img = algo(img)
    path = vectorization( img )
    # path = algo()
    path_to_font(path, current_glyph, tmp_font)

    # glyph_to_font_outline(font, tmp_font, current_glyph)
    img = glyph_to_raster(tmp_font, current_glyph)
    img = draw_points(path, img)
    return img

def algo(img):
    for gro in layers:
        for lay in gro:
            img = lay.run(img)
    return img

def modify_font():
    print("unprocessed glyphs :")
    for key in font.getGlyphSet():
        # if font["glyf"][glyph].isComposite() : return None # only with simple Glyphs
        if  key in list('qwertyuioplkjhgfdsazxcvbnmV'):
            img = glyph_to_raster(font, key)
            path = vectorization( algo(img) )
            path_to_font(path, key, font)
        # else:
        #     print(key, end=' ')  # check uncomputed glyph
    # if font['glyf'] : font['maxp'].recalc(font)
    font.save( utils.path("out.otf") )
    print("Modified font saved successfully!")

def new_layer(i):
    layer = len( layers[group] )
    layers[group].append( plugins[i].Layer() )
    layers[group][layer].gui_button = ttk.Checkbutton(gui.gui_frame_layer, text=names[i],style='Toggle.TButton', \
    command=partial(gui.select_layer,group, layer))
    layers[group][layer].gui_button.grid(column=group, row=layer, padx=15,pady=4)
    gui.select_layer(group, layer)
    print('NEW LAYER : ', names[i])
def new_group():
    layers.append( [] )
    global group
    global layer
    group += 1
    layer = -1
    new_layer(0)
    print('NEW GROUP : ', group)

def main():
    global root
    root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()
    gui.global_Interface(root)
    gui.load_new_font(utils.path("files/1.ttf"))
    gui.show_glyph()
    root.mainloop()
    print('main')



if __name__ == "__main__":
    print('RUN FROM MAIN')
    main()
