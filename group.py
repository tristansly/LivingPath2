# import gui_utils as gui
import gui
import main
import gui_utils
import utils
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from functools import partial

import cairo
from io import BytesIO
from PIL import Image
import pprint

class Group():

    def __init__(s):
        s.n = None
        s.layers = []
        s.gui_op = []
        s.op = 0
        s.outline_width = 100
        s.outline_join = 2
        s.outline_join_limit = 160000
        s.frame = ttk.Frame(gui.gui_frame_layer, style='Card.TFrame')
        for i in range(4) :
            s.gui_op.append( ttk.Button(s.frame, text=i, width=1.2) )
            s.gui_op[i].grid( row=i, column=0 )
            s.gui_op[i].config( command = partial(s.set_op, i) )
        s.gui_op_select = ttk.Button(s.frame, text=s.op, width=1.2, style='Toggle.TButton')
        s.gui_op_select.grid( row=i, column=0 )
        s.new_layer(0, refresh=False)

    def new_layer(s, i, refresh=True ):
        s.layers.append( main.plugins[i].Layer() )
        main.layer = s.layers[-1]
        main.layer.group = s
        main.layer.name = main.names[i]
        main.layer.setup_gui()
        main.layer.gui_position( len(s.layers)-1 )
        if refresh : main.select_layer( main.layer )
        if refresh : gui.refresh()
        if refresh : print(f'NEW LAYER : (G{s.n}) {main.names[i]}')

    def del_layer(s, layer):
        if len(s.layers) != 1 or s.n != 0 : # prevent delete 1st layer
            s.layers[layer].gui_frame.destroy()
            s.layers.pop(layer)
            for l in range(len(s.layers)): s.layers[l].gui_position(l)

            if len(s.layers) == 0 : main.del_group(s.n)
            if len(s.layers) == 0 and main.layer.group.n == s.n : main.select_layer( main.groups[0].layers[0])
            if main.layer.group.n == s.n and main.layer.n >= s.n: main.select_layer( main.groups[0].layers[0])

            print("DELETE : ",s.n,'(selected :', main.layer.group.n)
            gui.refresh()

    def position(s, n):
        s.n = n
        s.frame.grid( column=n, row=0, padx=15, pady=4 )

    def set_op(s, i):
        s.op = i
        gui.refresh()

    def gui(s, frame):
        gui_utils.Slider(frame, layer=s, max=200, name='outline_width' ).grid(column=1, row=7, sticky=tk.W)
        gui_utils.Slider(frame, layer=s, max=3, name='outline_join' ).grid(column=1, row=9, sticky=tk.W)
        gui_utils.Slider(frame, layer=s, max=300000, name='outline_join_limit' ).grid(column=1, row=10, sticky=tk.W)
