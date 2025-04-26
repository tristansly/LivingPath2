# import gui_utils as gui
import gui
import main
import utils
import gui_utils
from base_plugin import Plugin
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from functools import partial

from io import BytesIO
from PIL import Image, ImageTk
import pprint

class Group():

    def __init__(s):
        s.n = None
        s.layers = []
        s.op = 0
        s.gui_op, s.ico_on, s.ico_off = [], [], []
        s.op_frame = ttk.Frame(gui.gui_zone)
        s.drag_frame = None
        s.img = Image.new('L', (50, 50),(200))
        for i in range(5) :
            s.ico_on.append( gui_utils.get_img('op-on-'+str(i)+'.png', (20,20)) )
            s.ico_off.append( gui_utils.get_img('op-off-'+str(i)+'.png', (20,20)) )
            s.gui_op.append( ttk.Checkbutton( s.op_frame, style='no_indicatoron.TCheckbutton',takefocus=False,
                command = partial(s.set_op, i), image=s.ico_off[i]) )
            s.gui_op[i].grid( row=i, column=0, pady=0, ipady=0 )
            s.gui_op[i].bind('<Enter>',  partial(s.onEnter, i) )
            s.gui_op[i].bind('<Leave>',  partial(s.onLeave, i) )
        s.gui_op[s.op].config( image=s.ico_on[s.op] )

        print("new group position : ", s.n)
        s.position( len(main.groups) )
        print("new group position : ", s.n)
        s.new_layer(-1, ini=True)
        main.select_layer( s.layers[-1] )

    def new_layer(s, i, ini=False, refresh=True ):
        s.layers.append( Layer() if ini else main.plugins[i].Layer()  )
        main.layer = s.layers[-1]
        main.layer.ref_plugin = i
        main.layer.group = s
        main.layer.name = main.names[i] if not ini else "outline"
        main.layer.setup_gui()
        main.layer.gui_position( len(s.layers)-1 )
        main.select_layer( main.layer )
        if not ini and refresh : gui.refresh()
        print(f'NEW LAYER : (G{s.n}) {main.layer.name}')

    def del_layer(s, n, refresh=True):
        if len(s.layers) != 1 or s.n != 0 : # prevent delete 1st layer
            s.layers[n].frame.destroy()
            s.layers.pop(n)
            for l in range(len(s.layers)): s.layers[l].gui_position(l)
            main.over_layer = None

            if refresh :
                if len(s.layers) == 0 : main.del_group(s.n)
                if len(s.layers) == 0 and main.layer.group.n == s.n : main.select_layer( main.groups[0].layers[0])
                if main.layer.group.n == s.n and main.layer.n >= s.n: main.select_layer( main.groups[0].layers[0])
                gui.refresh()
            # else :
            #     main.del_group(s.n, select_last=False)

            print("DELETE LAYER :",s.n,'(selected group :', main.layer.group.n,')')

    def position(s, n):
        s.n = n
        for i, layer in enumerate(s.layers) :
            layer.set_main_frame()

        s.op_frame.grid_remove() if n == 0 else s.op_frame.grid( column=(n*2), row=0, sticky='n', rowspan='80', ipadx=0, ipady=0 )

    def set_op(s, op, refresh=True):
        s.op = op
        for i in range(5) : s.gui_op[i]['image'] = s.ico_on[i] if i==op else s.ico_off[i]
        print("SET OP : ",op)
        if refresh : gui.refresh()

    def img(s,img):
        gui.refresh_img(s.img, img)

    def onEnter(s, i, e): s.gui_op[i]['image'] = s.ico_on[i]
    def onLeave(s, i, e):
        if s.op != i: s.gui_op[i]['image'] = s.ico_off[i]

    def gost(s):
        b = object.__new__(Group)
        b.__dict__ = s.__dict__.copy()
        b.op_frame = b.drag_frame = b.gui_op = b.ico_on = b.ico_off =  42

        b.layers = []
        for l in s.layers:
            b.layers.append( l.gost() )
        return b


class Layer(Plugin):
    """outline font group"""

    def __init__(s):
        super(Layer, s).__init__()

    def gui(s, frame):
        gui_utils.Checkbutton(frame, layer=s, name='outline',                ini=False ).pack(anchor='w')
        gui_utils.Slider(frame, layer=s, max=200, name='outline_width',      ini=100   ).pack(anchor='w')

        s.gui_join = gui_utils.Optionbutton(frame, layer=s, nbr=3, ini=2, pos='inline', name='corner_join', img_name='join' )
        s.gui_join.callback = partial(s.set_limit, s.gui_join )
        s.gui_join.pack(anchor='w', pady=(25,0))

        s.gui_limit_join= gui_utils.Slider(frame, layer=s, max=160, name='corner_join_limit', ini=100)
        s.gui_limit_join.pack(anchor='w')


    def set_limit(s,x):
        print(x.var)
        if int(x.var) == 2 : gui_utils.switch(s.gui_limit_join, flag=True)
        else :              gui_utils.switch(s.gui_limit_join, flag=False)
    def run(s, img):
        return img

    def get_img(s):
        return img
