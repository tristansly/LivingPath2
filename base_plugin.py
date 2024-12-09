# import gui_utils as gui
import gui
import main
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from functools import partial
import group

from PIL import Image

class Plugin(object):
    """Base plugin."""

    def __init__(s):
        s.group = None
        s.n = None
        s.active=True
        s.img = None

    def setup_gui(s):
        s.frame = ttk.Frame(gui.gui_zone)
        s.frame.bind("<Enter>", lambda _: s.enter_btn())
        s.frame.bind("<Leave>", lambda _: s.leave_btn())

        s.gui_button = ttk.Checkbutton(s.frame, text=s.name.replace('_',' '), style='Toggle.TButton', width=20)
        s.gui_button.grid( column=1, row=0, padx=2, pady=2, sticky="nsew" )
        s.gui_drag = ttk.Button(s.frame, text="lll" ,width=1.2)
        s.gui_del = ttk.Button(s.frame, text="X", width=1.2)
        s.gui_toggle = ttk.Button(s.frame, text='O', width=1.2, command = s.toogle)

        if s.name=='outline' and s.group.n==0 : s.gui_del["style"] = 'none.TButton' # delete btn of 1st group
        if s.name!='outline' : s.gui_drag.grid( column=0, row=0, padx=2, pady=2, sticky="nsew" )
        if s.name!='outline' : s.gui_toggle.grid( column=2, row=0, padx=2, pady=2 )
        s.gui_del.grid( column=3, row=0, padx=2, pady=2 )

    def toogle(s):
        s.active = not s.active
        if s.active :     s.gui_toggle["style"] = 'azure.TButton' # s.gui_toggle.configure(text='⋁')
        if not s.active : s.gui_toggle["style"] = 'none.TButton' # s.gui_toggle.configure(text='∵')
        gui.refresh()

    def gui_position(s, n, group=None ):
        if group : s.group = group
        s.n = n
        s.frame.grid( column=(s.group.n*2), row=n, padx=15, pady=4, sticky="" )
        s.gui_button.config( command = partial(main.select_layer, s) )
        if s.name!='outline' : s.gui_del.config( command = partial(s.group.del_layer, s.n) )
        if s.name=='outline' : s.gui_del.config( command = partial(main.del_group, s.group) )

        print("LAYER POS :", n, " ", s.name, end=' ' )

    def change_order(s, group, layer, refresh=True):
        print("DROP LAYER POS : ",s.group.n, s.n," -> ", group, layer )
        x = s.group.layers.pop( s.n )
        main.groups[group].layers.insert( layer, x )

        for g in main.groups :
            for i, l in enumerate(g.layers) :
                l.gui_position(i, g)
                print("changeOrder : ",g.n, i )
        main.select_layer(main.groups[group].layers[layer])
        if refresh : gui.refresh()


    def gui_img(img):
        img_min = ImageTk.PhotoImage( img.crop((150, 150, img.width-150, img.height-150)).resize((20,20),1) )
        gui_button.configure(image=img_min)
        gui_button.image = img_min

    def gui(s, frame): None
    def run(s, img): return img

    def save(s, img):
        s.img = img

    def gost(s):
        # print("mnamw", main.plugins[s.ref_plugin], type(s).__name__, s.ref_plugin)
        if s.ref_plugin == -1 : b = object.__new__(group.Layer)
        if s.ref_plugin != -1 : b = object.__new__(main.plugins[s.ref_plugin].Layer)
        b.__dict__ = s.__dict__.copy()
        b.gui_button = b.gui_drag = b.frame = b.gui_del = b.group =42

        return b

    def enter_btn(s):
        main.over_layer = s
        gui.refresh(compute=False)
    def leave_btn(s):
        main.over_layer = None
        gui.refresh(compute=False)
