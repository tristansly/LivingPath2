import utils, wiki
from font_utils import *
import path_utils
import gui
import gui_utils
from group import Group
from base_plugin import Plugin
from tkinterdnd2 import DND_FILES, TkinterDnD
from fontTools import ttLib
from functools import partial
import PIL
import math, os
import string
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
    if not msg :
        print("["+current_glyph+"] ",end='')
        last_time = 0
    if msg == "end": print("")
    elif msg : print( msg+':',str(perf_counter()-last_time).replace('0','-')[0:5], end='  ' )
    last_time = perf_counter()

def get_current_img( key, visual_info=True ):
    time(None)
    global img
    for g in groups: # apply algos to pixels
        img = glyph_to_img_outline(key, font, g)
        for l in g.layers:
            if l.active :
                img = l.run_and_save(img)
        if g.n > 0 : img = operator_img(img, prev_img, g.op)
        prev_img = img
    time("algo")

    if params.display_points and visual_info :
        path = vectorization( img )
        time("vecto")
        path_to_font(path, key, tmp_font) # .002 sec
        img = draw_points(path, img)
    if params.display_rules and visual_info :
        img = draw_rules(img, key, font )
    time("end")
    if visual_info :
        mask = PIL.ImageOps.invert(layer.img).point(lambda i: i//3)
        img = img.convert('RGB')
        img.paste((80,160,255), (0,0), mask )
    return img

def process_to_path(args):
    (key, param, groups, font) = args
    for g in groups: # apply algos to pixels
        img = glyph_to_img_outline(key, font, g)
        for l in g.layers:
            if l.active : img = l.run(img)
        if g.n > 0 : img = operator_img(img, prev_img, g.op)
        prev_img = img
    return (vectorization(img, param), key)


import multiprocessing as multi
def text_to_font(txt, out_font, char_to_glyph=True):
    if char_to_glyph : # remove glyphs allready computed
        txt = utils.get_used_glyphs(txt, font, hbfont)
        gui_utils.used_glyphs.append('space')
        for i in gui_utils.used_glyphs:
            txt2 = [j for j in txt if j != i]
            txt = txt2

    time(None) # without multi
    for i, key in enumerate(txt):
        gui.root.update()
        gui.root.title( 'LivingPath - Computed glyphs '+str(i)+'/'+str(len(txt)) )
        path_to_font(vectorization(get_current_img(key,visual_info=False)),key, out_font)
    gui.root.title( 'LivingPath' )
    time("End without multiprocess")

    # time(None) # pool
    # gost_groups = [g.gost() for g in groups]
    # args = [(key, params, gost_groups, font) for key in txt]
    # with multi.Pool( utils.constrain(len(txt),2,multi.cpu_count()-1) ) as p:
    #     result = p.map(process_to_path, args, chunksize=10)
    #     p.terminate()
    # for r in result:
    #     path_to_font(r[0], r[1], out_font)
    # time('Pool[ glyph: '+str(len(txt))+' process: '+str(utils.constrain(len(txt),2,multi.cpu_count()-1))+']')

    gui_utils.used_glyphs += txt

def process_font_export(path='', name=None, style=None ):
    global font
    gs = {k: v for k, v in font.getGlyphSet().items() if k in string.ascii_lowercase } # filter
    text_to_font(gs, font, char_to_glyph=False)

    # for key in font.getGlyphSet():
    #     # if font["glyf"][glyph].isComposite() : return None # only with simple Glyphs
        # if True: # key in list( set(txt) ):
        #     print(key)
        # else:
        #     print(key, end=' ')  # check uncomputed glyph
    # if font['glyf'] : font['maxp'].recalc(font)

    rename_font(font, name, style )
    font.save( utils.path( path )  )
    font = copy.deepcopy(font_origin)
    time("Font saved : "+ path)

def select_layer( selected ):
    global layer
    layer = selected
    for child in gui.gui_para.content.winfo_children(): child.destroy()
    for grp in groups :
        for lay in grp.layers :
            lay.gui_button.state(["!selected"])
    layer.gui_button.state(["selected"])
    layer.gui( gui.gui_para.content )
    gui.gui_para.updateContent()

    print('SELECT_LAYER : group',layer.group.n,' - layer', layer.n)

def new_layer(i, refresh=True):
    print('SELECT_LAYER : group',layer.group.n,' - layer', layer.n)
    layer.group.new_layer(i, refresh=refresh)

def new_group():
    groups.append( Group() )
    print('NEW GROUP : ', layer.group.n)

def del_group(n, select_last=True):
    print('DELETE GROUP : ', n)
    g = groups[n]
    for l in reversed(g.layers) : g.del_layer(l.n, False)
    if g.op_frame :   g.op_frame.destroy()
    if g.drag_frame : g.drag_frame.destroy()
    del groups[n]
    for i in range(len(groups)) : groups[i].position(i)
    if select_last :
        if layer.group.n == n : select_layer( groups[0].layers[-1] )
    gui.refresh()

def duplicate_layer( g=None, refresh=True ):
    if g==None : g = layer.group
    l_old = layer
    g.new_layer(layer.ref_plugin, refresh=False)

    for name, val in utils.get_layer_attr( l_old ):
        setattr(layer, name, val)
    layer.gui( gui.gui_para.content )
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
    gui.root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()
    gui.root.config(cursor="watch");
    gui.global_Interface(gui.root)
    wiki.get_wiki_langs()
    wiki.set_wiki_lang('fr')
    gui.load_new_font(utils.path("files/1.otf"))
    gui.root.config(cursor="")

    gui.root.mainloop()

if __name__ == "__main__":
    # multi.freeze_support() # multiprocessing compatibility for pyinstaller
    print('RUN FROM MAIN')
    main()
