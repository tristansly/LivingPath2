import utils, wiki
from font_utils import *
import path_utils
import gui
from group import Group
from base_plugin import Plugin

from tkinterdnd2 import DND_FILES, TkinterDnD
from fontTools import ttLib
from functools import partial
import PIL
import math, os
import copy

import pprint

plugins, names, groups = [], [], []
layer = None
current_glyph = 'g'
root = None
font = ttLib.TTFont(utils.path("files/1.ttf"), recalcBBoxes=False)
font_origin = ttLib.TTFont(utils.path("files/1.ttf"), recalcBBoxes=False)
tmp_font = ttLib.TTFont(utils.path("files/1.ttf"), recalcBBoxes=False)
hbfont = None
img = PIL.Image.new("L", (200, 200)) # ini img

from time import perf_counter
def time(msg):
    global last_time
    if msg : print(' | ', str(perf_counter()-last_time).replace('0','-')[0:5],msg,end='' )
    if not msg : print("\nTIMER : ",end='')
    last_time = perf_counter()

def get_current_img( key ):
    # time(None)
    global img
    for g in groups: # apply algos to pixels
        img = glyph_to_img_outline(key, font, g)
        for l in g.layers:
            img = l.run(img)
        if g.n > 0 : img = operator_img(img, prev_img, g.op)
        prev_img = img
    # time("algo")

    if params.display_points :
        path = vectorization( img )
        # time("vecto")
        path_to_font(path, key, tmp_font) # .002 sec
        img = draw_points(path, img)
        # time("display vecto")
    return img

def process_to_path(args):
    (key, param, groups, font) = args
    for g in groups: # apply algos to pixels
        img = glyph_to_img_outline(key, font, g)
        for l in g.layers:
            img = l.run(img)
        if g.n > 0 : img = operator_img(img, prev_img, g.op)
        prev_img = img

    return (vectorization(img, param), key)


import multiprocessing as multi
def text_to_font(txt, out_font, used_glyphs=[], char_to_glyph=True):
    if char_to_glyph : # remove glyphs allready computed
        txt = utils.get_used_glyphs(txt, font, hbfont)
        used_glyphs.append('space')
        for i in used_glyphs:
            txt2 = [j for j in txt if j != i]
            txt = txt2

    # time(None) # without multi
    # for key in txt:
    #     path_to_font(vectorization(get_current_img(key)),key, out_font)
    # time("End without multiprocess")

    time(None) # pool
    gost_groups = [g.gost() for g in groups]
    args = [(key, params, gost_groups, font) for key in txt]
    with multi.Pool( utils.constrain(len(txt),2,multi.cpu_count()-1) ) as p:
        result = p.map(process_to_path, args, chunksize=10)
        p.terminate()
    for r in result:
        path_to_font(r[0], r[1], out_font)
    time(' with pool, nbr glyph : '+str(len(txt))+' process : '+str(utils.constrain(len(txt),2,multi.cpu_count()-1)))

    return txt

def modify_font(txt=list('qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM'), name='out.ttf'):
    txt.extend(["eacute","egrave"])
    # print("unprocessed glyphs :")
    global font
    # text_to_font(font.getGlyphSet(), font)
    text_to_font(txt, font, char_to_glyph=False)
    # for key in font.getGlyphSet():
    #     # if font["glyf"][glyph].isComposite() : return None # only with simple Glyphs
        # if True: # key in list( set(txt) ):
        #     print(key)
        # else:
        #     print(key, end=' ')  # check uncomputed glyph
    # if font['glyf'] : font['maxp'].recalc(font)
    name = 'livingPath test '+random(9999)
    font_utils.rename_font(name)
    font.save( utils.path(name + '.otf')  )
    font = copy.deepcopy(font_origin)
    time("Font saved : name")
    print()

def select_layer( selected ):
    global layer
    layer = selected
    for child in gui.gui_para.winfo_children(): child.destroy()
    for grp in groups :
        for lay in grp.layers :
            lay.gui_button.state(["!selected"])
    layer.gui_button.state(["selected"])
    layer.gui( gui.gui_para )
    print('SELECT_LAYER : group',layer.group.n,' - layer', layer.n)

def new_layer(i, refresh=True):
    print('SELECT_LAYER : group',layer.group.n,' - layer', layer.n)
    layer.group.new_layer(i, refresh=refresh)

def new_group():
    groups.append( Group() )
    print('NEW GROUP : ', layer.group.n)

def del_group(n, select_last=True):
    print('DELETE GROUP : ', n)
    if groups[n].op_frame :   groups[n].op_frame.destroy()
    if groups[n].drag_frame : groups[n].drag_frame.destroy()
    del groups[n]
    for i in range(len(groups)) : groups[i].position(i)
    if select_last :
        if layer.group.n == n : select_layer( groups[0].layers[-1] )

def duplicate_layer( g=None, refresh=True ):
    if g==None : g = layer.group
    l_old = layer
    g.new_layer(layer.ref_plugin, refresh=False)

    for name, val in utils.get_layer_attr( l_old ):
        setattr(layer, name, val)
    layer.gui( gui.gui_para )
    select_layer(layer)
    if refresh : gui.refresh()

def duplicate_group():
    g_old = layer.group
    new_group()
    for name, val in utils.get_layer_attr( g_old.layers[0] ): setattr(layer, name, val) # setup outline param
    for l in g_old.layers[1:] :
        select_layer(l)
        duplicate_layer( g = groups[-1], refresh=False )


def main():
    root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()
    gui.global_Interface(root)
    wiki.set_wiki_lang('fr')
    gui.load_new_font(utils.path("files/1.otf"))

    root.mainloop()


if __name__ == "__main__":
    multi.freeze_support() # multiprocessing compatibility for pyinstaller
    print('RUN FROM MAIN')
    main()
