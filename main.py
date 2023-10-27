import utils
from font_utils import *
import font_utils
import gui
from group import Group

from base_plugin import Plugin

from tkinterdnd2 import DND_FILES, TkinterDnD
import math, os
from fontTools import ttLib
from functools import partial
import pprint

plugins, names, groups = [], [], []
layer = None
current_glyph = 'g'
root = None
font = ttLib.TTFont(utils.path("files/1.ttf"), recalcBBoxes=False)
tmp_font = ttLib.TTFont(utils.path("files/1.ttf"), recalcBBoxes=False)
img = glyph_to_img(font, current_glyph)


from time import perf_counter
def time(msg):
    global last_time
    if msg : print( str(perf_counter()-last_time).replace('0','-')[0:5],msg,end='' )
    if not msg : print("\nTIMER : ",end='')
    last_time = perf_counter()

def get_current_img():
    time(None)
    # img = glyph_to_img(font, current_glyph)
    # img = glyph_to_img_outline(font, current_glyph)

    for g in groups:
        glyph_to_font_outline(current_glyph, font, tmp_font, g) # .002 sec
        # glyph_to_font_outline(font, tmp_font, current_glyph, g) # .002 sec
        img = glyph_to_img(tmp_font, current_glyph) # .009 sec
        for l in g.layers:
            img = l.run(img)
        if g.n > 0 :
            img = operator_img(img, prev_img, g.op)
        prev_img = img
    time(" algo ")

    if font_utils.display_points :
        path = vectorization( img )
        # time(" vecto ")
        path_to_font(path, current_glyph, tmp_font) # .002 sec
        img = glyph_to_img(tmp_font, current_glyph) # .006 sec
        img = draw_points(path, img)
        time(" display vecto ")
    return img

def algo(img):
    for g in groups:
        for l in g.layers:
            img = l.run(img)
    return img

def modify_font():
    print("unprocessed glyphs :")
    for key in font.getGlyphSet():
        # if font["glyf"][glyph].isComposite() : return None # only with simple Glyphs
        if  key in list('qwertyuioplkjhgfdsazxcvbnmV'):
            img = glyph_to_img(font, key)
            path = vectorization( algo(img) )
            path_to_font(path, key, font)
        # else:
        #     print(key, end=' ')  # check uncomputed glyph
    # if font['glyf'] : font['maxp'].recalc(font)
    font.save( utils.path("out.otf") )
    print("Modified font saved successfully!")

def select_layer( selected ):
    global layer
    layer = selected
    for child in gui.gui_frame_param.winfo_children(): child.destroy()
    for grp in groups :
        for lay in grp.layers :
            lay.gui_button.state(["!selected"])
    layer.gui_button.state(["selected"])
    layer.gui( gui.gui_frame_param )
    print('( select_layer : group',layer.group.n,' - layer', layer.n,')')

def new_layer(i, refresh=True):
    print('( new_layer : group',layer.group.n,' - layer', layer.n,')')
    layer.group.new_layer(i)
    # groups[0].new_layer(i)

def new_group():
    groups.append( Group() )
    select_layer( groups[-1].layers[-1] )
    groups[-1].position( len(groups)-1 )
    print('NEW GROUP : ', layer.group.n)

def del_group(n):
    groups[n].frame.destroy()
    groups.pop( n )
    for i in range(len(groups)) : groups[i].position(i)
    if layer.group.n == n : select_layer( groups[0].layers[-1] )

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
