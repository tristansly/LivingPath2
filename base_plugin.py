# import gui_utils as gui
import gui
import main
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from functools import partial

import cairo
from io import BytesIO
from PIL import Image
import pprint

class Plugin():
    """Base plugin."""

    def __init__(s):
        s.group = None
        s.n = None

    def setup_gui(s):
        s.gui_frame = ttk.Frame(s.group.frame, style='Card.TFrame')

        s.gui_button = ttk.Checkbutton(s.gui_frame, text=s.name, style='Toggle.TButton', compound='left')
        s.gui_button.grid( column=1, row=0, padx=2, pady=2 )

        s.gui_del = ttk.Button(s.gui_frame, text="X", width=1.2, style='Toggle.TButton')
        s.gui_del.grid( column=2, row=0, padx=2, pady=2 )

        s.gui_drag = ttk.Button(s.gui_frame, text="lll", width=1.2, style='Toggle.TButton')
        s.gui_drag.grid( column=0, row=0, padx=2, pady=2 )
    def gui_position(s, n):
        s.n = n
        # s.gui_frame.grid_forget()
        s.gui_frame.grid( column=0, row=n, padx=15, pady=4 )
        s.gui_button.config( command = partial(main.select_layer, s) )
        # s.gui_button.state(["!selected"])
        s.gui_del.config( command = partial(s.group.del_layer, s.n) )

    def gui_img(img):
        img_min = ImageTk.PhotoImage( img.crop((150, 150, img.width-150, img.height-150)).resize((20,20),1) )
        gui_button.configure(image=img_min)
        gui_button.image = img_min
    def gui(s, frame):
        None
