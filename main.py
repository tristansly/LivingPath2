import utils
from font_utils import *
import font_utils
import gui
from group import Group
from base_plugin import Plugin

from tkinterdnd2 import DND_FILES, TkinterDnD
from fontTools import ttLib
from functools import partial
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
img = glyph_to_img(font, current_glyph)

from time import perf_counter
def time(msg):
    global last_time
    if msg : print(' | ', str(perf_counter()-last_time).replace('0','-')[0:5],msg,end='' )
    if not msg : print("\nTIMER : ",end='')
    last_time = perf_counter()

def get_current_img( key ):
    # time(None)
    global img
    for g in groups:
        # glyph_to_font_outline(current_glyph, font, tmp_font_ttf, g) # .002 sec
        # img = glyph_to_img(tmp_font_ttf, current_glyph) # .009 sec
        img = glyph_to_img_outline(key, font, g)

        for l in g.layers: img = l.run(img)
        if g.n > 0 :
            img = operator_img(img, prev_img, g.op)
        prev_img = img
    # time("algo")

    if font_utils.display_points :
        path = vectorization( img )
        # time("vecto")
        path_to_font(path, key, tmp_font) # .002 sec
        img = draw_points(path, img)
        # time("display vecto")
    return img

def process_to_path(key,f):
    global img
    for g in groups:
        # glyph_to_font_outline(current_glyph, font, tmp_font_ttf, g) # .002 sec
        # img = glyph_to_img(tmp_font_ttf, current_glyph) # .009 sec
        img = glyph_to_img_outline(key, f, g)

        for l in g.layers: img = l.run(img)
        if g.n > 0 :
            img = operator_img(img, prev_img, g.op)
        prev_img = img

    print(key)
    return ( key, vectorization(img) )


from multiprocessing import Pool, cpu_count
def text_to_img(txt):
    time(None)
    # global tmp_font
    # pool = Pool(processes=(cpu_count() - 1)) # multiprocess
    # for key in list(set(txt)):
    #     pool.apply_async( process_to_path, args=(key,tmp_font) )
    # # results = pool.starmap( process_to_path, zip(list(set(txt)),[tmp_font for i in range(len(set(txt)))]) )
    # results = [pool.apply_async(process_to_path, (key,tmp_font)) for key in list(set(txt))]
    # pool.close()
    # results = [res.get() for res in results]
    # # for path, key in zip( results, list(set(txt)) ) : path_to_font(path, key, tmp_font)
    # for n in range(len(set(txt))) :
    #     print(results[n])
    #     path_to_font(results[n][1], results[n][0], tmp_font)

    for key in list(set(txt)): # without multiprocess
        path_to_font(process_to_path(key,font)[1], key, tmp_font)
        # gui.refresh_img(gui.img_letter, text_to_img_HB(txt, tmp_font, hbfont)) // dont work...

    time("End multiprocess")
    img = text_to_img_HB(txt, tmp_font, hbfont)
    time("txt to img")
    return img

def modify_font(txt='qwertyuioplkjhgfdsazxcvbnmV', name='out.otf'):
    # print("unprocessed glyphs :")
    global font
    for key in font.getGlyphSet():
        # if font["glyf"][glyph].isComposite() : return None # only with simple Glyphs
        if key in list( set(txt) ):
            img = get_current_img(key)
            path = vectorization( img )
            path_to_font(path, key, font)
        # else:
        #     print(key, end=' ')  # check uncomputed glyph
    # if font['glyf'] : font['maxp'].recalc(font)
    font.save( utils.path(name) )
    print("Modified font saved successfully!")
    font = copy.deepcopy(font_origin)

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

def new_layer(i):
    print('SELECT_LAYER : group',layer.group.n,' - layer', layer.n)
    layer.group.new_layer(i)

def new_group():
    groups.append( Group() )
    print('NEW GROUP : ', layer.group.n)

def del_group(n):
    if groups[n].op_frame :   groups[n].op_frame.destroy()
    if groups[n].drag_frame : groups[n].drag_frame.destroy()
    groups.pop( n )
    for i in range(len(groups)) : groups[i].position(i)
    if layer.group.n == n : select_layer( groups[0].layers[-1] )

def main():
    root = TkinterDnD.Tk()  # notice - use this instead of tk.Tk()
    gui.global_Interface(root)
    gui.load_new_font(utils.path("files/1.otf"))
    # gui.show_glyph()


    root.mainloop()
    print('main')

    # modify_font()


if __name__ == "__main__":
    print('RUN FROM MAIN')
    main()
