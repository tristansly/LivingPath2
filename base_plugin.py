# import gui_utils as gui
import gui
import main
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from functools import partial

import cairo
from io import BytesIO
from PIL import Image
import pprint

class plugin():
    """Base plugin."""

    def __init__(s):
        s.group = main.group
        s.layer = main.layer

    def setup_gui(s):
        s.gui_frame = ttk.Frame(gui.gui_frame_layer, style='Card.TFrame')
        s.gui_frame.grid( column=s.group, row=s.layer, padx=15, pady=4 )

        s.gui_button = ttk.Checkbutton(s.gui_frame, text=s.name, style='Toggle.TButton', compound='left')
        s.gui_button.config( command = partial(gui.select_layer,s.group,s.layer) )
        s.gui_button.grid( column=1, row=0, padx=2, pady=2 )

        s.gui_del = ttk.Button(s.gui_frame, text="X", style='Toggle.TButton')
        s.gui_del.config( command = partial(main.del_layer,s.group,s.layer) )
        s.gui_del.config( width=1)
        s.gui_del.grid( column=2, row=0, padx=2, pady=2 )

    def gui_position(s, group, layer):
        s.group = group
        s.layer = layer
        # s.gui_frame.grid_forget()
        s.gui_frame.grid( column=group, row=layer, padx=15, pady=4 )
        s.gui_button.config( command = partial(gui.select_layer,s.group,s.layer) )
        s.gui_del.config( command = partial(main.del_layer,s.group,s.layer) )

    def gui_img(img):
        img_min = ImageTk.PhotoImage( img.crop((150, 150, img.width-150, img.height-150)).resize((20,20),1) )
        gui_button.configure(image=img_min)
        gui_button.image = img_min
