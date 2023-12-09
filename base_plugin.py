# import gui_utils as gui
import gui
import main
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from functools import partial

from PIL import Image

class Plugin():
    """Base plugin."""

    def __init__(s):
        s.group = None
        s.n = None

    def setup_gui(s):
        s.frame = ttk.Frame(gui.gui_zone)

        s.gui_button = ttk.Checkbutton(s.frame, text=s.name.replace('_', ' '), style='Toggle.TButton')
        s.gui_button.grid( column=1, row=0, padx=2, pady=2 )

        s.gui_del = ttk.Button(s.frame, text="X", width=1.2, style='Toggle.TButton')
        s.gui_del.grid( column=2, row=0, padx=2, pady=2 )

        s.gui_drag = ttk.Button(s.frame, text="lll", width=1.2, style='Toggle.TButton')
        s.gui_drag.grid( column=0, row=0, padx=2, pady=2 )

    def gui_position(s, n, group=None ):
        if group : s.group = group
        s.n = n
        s.frame.grid( column=(s.group.n*2), row=n, padx=15, pady=4 )
        s.gui_button.config( command = partial(main.select_layer, s) )
        s.gui_del.config( command = partial(s.group.del_layer, s.n) )
        print("LAYER POS :", n, " ", s.name, end=' ' )

    def change_order(s, group, layer):
        print("DROP LAYER POS : ",s.group.n, s.n," -> ", group, layer )
        x = s.group.layers.pop( s.n )
        main.groups[group].layers.insert( layer, x )

        for g in main.groups :
            for i, l in enumerate(g.layers) :
                l.gui_position(i, g)
                print("changeOrder : ",g.n, i )
            g.set_drag_zone()
        gui.refresh()


    def gui_img(img):
        img_min = ImageTk.PhotoImage( img.crop((150, 150, img.width-150, img.height-150)).resize((20,20),1) )
        gui_button.configure(image=img_min)
        gui_button.image = img_min

    def gui(s, frame):
        None
