from utils import *
import font_utils, gui

import tkinter as tk
from tkinter import TclError, ttk, Tk, Frame, Menu, Label, Entry
import inspect

class Slider(ttk.Frame):
    def __init__(s, context, size=200, min=0, max=100, layer=None, name='', format="%d", flag='', ini=0):
        super(Slider, s).__init__(context)
        s.format = format
        s.name = name.replace(' ', '_')
        s.flag = flag
        s.layer = font_utils if layer == None else layer
        if not hasattr(s.layer, s.name) : s.set_attach_val(ini) # set ini only at layer init

        s.val = ttk.Label(s, text = s.format % s.get_attach_val()) # display fix slider number
        s.val.grid(column=1, row=1, sticky=tk.W, padx=5 )

        s.slider = ttk.Scale(s, from_=min, to_=max, length=size, orient="horizontal",style='Tick.TScale')
        s.slider.set( s.get_attach_val() )
        s.slider.configure(command = s.update)
        s.slider.bind("<ButtonRelease-1>", s.update_eco)
        s.slider.grid(column=0, row=1, sticky=tk.W)

        s.title = ttk.Label(s, text = name.replace('_', ' ') )
        s.title.grid(column=0, row=0, sticky=tk.W)

    def update(s, event):
        s.val.configure(text=s.get())
        if ( s.flag!='eco' ) and getattr( s.layer, s.name )!= None :
        # if ( s.flag!='eco' and not font_utils.display_points ) and getattr( s.layer, s.name )!= None :
            s.set_attach_val()
            gui.show_glyph()
    def update_eco(s, event):
        if ( s.flag=='eco' ) and getattr( s.layer, s.name )!= None :
        # if ( s.flag=='eco' or font_utils.display_points ) and getattr( s.layer, s.name )!= None :
            s.set_attach_val()
            gui.show_glyph()

    def set_attach_val(s, val=None ):
        if val==None : val = s.get() # if not ini
        if s.format == "%d" : setattr(s.layer, s.name, int(val))
        if s.format != "%d" : setattr(s.layer, s.name, float(val))
    def get_attach_val(s):
        return getattr(s.layer, s.name)
    def get(s):
        return s.format % float( s.slider.get() )

class Checkbutton(ttk.Frame):
    def __init__(s, context, layer=None, name='', ini=False):
        super(Checkbutton, s).__init__(context)
        s.name = name
        s.layer = font_utils if layer == None else layer
        s.var = tk.StringVar()
        if not hasattr(s.layer, s.name) : s.set_attach_val(ini) # set ini only at layer init
        s.var.set( s.get_attach_val() )
        s.check = ttk.Checkbutton( s, text=name.replace('_',' '), variable=s.var )
        s.check.configure(command = s.update)
        s.check.grid(column=0, row=1, sticky=tk.W)

    def update(s, val='undefined'):
        if getattr( s.layer, s.name ) != None and val != int(s.var.get()):
            if val != 'undefined': s.var.set(val)
            s.set_attach_val()
            gui.show_glyph()

    def set_attach_val(s, val=False):
        if not val : val = s.var.get()
        setattr(s.layer, s.name, int(val or 0))

    def get_attach_val(s):
        return getattr(s.layer, s.name)

#----------------------------------------------------------------------------------

# def get_calling_module():
#     name = inspect.getmodule(inspect.stack()[2][0]).__name__.split('.')[-1]
#     print('get calling module', name)
#     return font_utils if name == 'gui' else get_plugin(name)

#----------------------------------------------------------------------------------
