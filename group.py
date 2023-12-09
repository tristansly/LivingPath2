# import gui_utils as gui
import gui
import main
import gui_utils
import utils
from base_plugin import Plugin
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from functools import partial

import cairo
from io import BytesIO
from PIL import Image, ImageTk
import pprint

class Group():

    def __init__(s):
        s.n = None
        s.layers = []
        s.op = 0
        s.gui_op, s.ico_on, s.ico_off = [], [], []
        s.op_frame = ttk.Frame(gui.gui_zone, style='Card.TFrame')
        s.drag_frame = None
        s.img = Image.new('L', (50, 50),(200))
        for i in range(5) :
            s.ico_on.append( ImageTk.PhotoImage(Image.open(utils.path('files/theme/op-on-'+str(i)+'.png')).resize((20, 20), Image.NEAREST)) )
            s.ico_off.append(ImageTk.PhotoImage(Image.open(utils.path('files/theme/op-off-'+str(i)+'.png')).resize((20, 20), Image.NEAREST)) )
            s.gui_op.append( ttk.Checkbutton( s.op_frame, width=1.2, style='no_indicatoron.TCheckbutton',
                command = partial(s.set_op, i), image=s.ico_off[i], compound="left", takefocus=False) )
            s.gui_op[i].grid( row=i, column=0 )
        s.gui_op[s.op].config( image=s.ico_on[s.op] )

        s.position( len(main.groups) )
        s.new_layer(0, ini=True)
        main.select_layer( s.layers[-1] )

    def new_layer(s, i, ini=False ):
        s.layers.append( Layer() if ini else  main.plugins[i].Layer()  )
        main.layer = s.layers[-1]
        main.layer.group = s
        main.layer.name = main.names[i] if not ini else "outline"
        main.layer.setup_gui()
        main.layer.gui_position( len(s.layers)-1 )
        main.select_layer( main.layer )
        s.set_drag_zone()
        if not ini : gui.refresh()
        print(f'NEW LAYER : (G{s.n}) {main.layer.name}')

    def set_drag_zone(s):
        if s.drag_frame : s.drag_frame.destroy()
        s.drag_frame = ttk.Frame(gui.gui_zone) # style='Card.TFrame'
        s.drag_frame.grid( column=s.n*2, row=len(s.layers), rowspan=20, sticky='nsew' )
        # gui.gui_zone.rowconfigure(s.n*2, weight=3-len(s.layers) )

    def del_layer(s, layer):
        if len(s.layers) != 1 or s.n != 0 : # prevent delete 1st layer
            s.layers[layer].frame.destroy()
            s.layers.pop(layer)
            for l in range(len(s.layers)): s.layers[l].gui_position(l)
            s.set_drag_zone()

            if len(s.layers) == 0 : main.del_group(s.n)
            if len(s.layers) == 0 and main.layer.group.n == s.n : main.select_layer( main.groups[0].layers[0])
            if main.layer.group.n == s.n and main.layer.n >= s.n: main.select_layer( main.groups[0].layers[0])

            print("DELETE : ",s.n,'(selected :', main.layer.group.n)
            gui.refresh()

    def position(s, n):
        s.n = n

        for i, layer in enumerate(s.layers) :
            layer.frame.grid( column=n*2, row=i, padx=15, pady=4 )

        print("position : ", n)
        s.op_frame.grid_remove() if n == 0 else s.op_frame.grid( column=(n*2)-1, row=0, sticky='nsew', rowspan='20' )

    def set_op(s, op):
        s.op = op
        for i in range(5) : s.gui_op[i]['image'] = s.ico_on[i] if i==op else s.ico_off[i]
        print("SET OP : ",op)
        gui.refresh()

    def img(s,img):
        gui.refresh_img(s.img, img)


class Layer(Plugin):
    """outline font group"""

    def __init__(s):
        super(Layer, s).__init__()

    def gui(s, frame):
        gui_utils.Checkbutton(frame, layer=s, name='outline',                   ini=False ).grid(column=0, row=0, sticky='ew')
        gui_utils.Slider(frame, layer=s, max=200, name='outline_width',         ini=100   ).grid(column=0, row=1, sticky='ew')
        gui_utils.Slider(frame, layer=s, max=3, name='outline_join',            ini=2     ).grid(column=0, row=2, sticky='ew')
        gui_utils.Slider(frame, layer=s, max=300000, name='outline_join_limit', ini=160000).grid(column=0, row=3, sticky='ew')

    def run(s, img):
        return img
