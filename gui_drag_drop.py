
from tkinter import *
from functools import partial

from tkinter import Button, Label, Entry, Tk, SE, ttk
from PIL import ImageTk, Image
import main
import gui

def changeOrder(widget1, widget2, initial):
    target=widget1.grid_info()
    widget1.grid(row=initial['row'], column=initial['column'])
    widget2.grid(row=target['row'], column=target['column'])

def on_click(event):
    btn = event.widget
    frame = event.widget.master
    print('drag',btn)
    if isinstance(btn, ttk.Button) and btn['text'] == 'lll':
        start = (event.x,event.y)
        grid_info = frame.grid_info()
        btn.bind("<B1-Motion>", lambda event:drag_motion(event, frame, start))
        btn.bind("<ButtonRelease-1>", lambda event:drag_release(event, frame, grid_info))
    else:
        gui.gui_frame_layer.unbind("<ButtonRelease-1>")

def drag_motion(event, frame, start):
    x = frame.winfo_x()+event.x-start[0]
    y = frame.winfo_y()+event.y-start[1]
    frame.lift()
    frame.place(x=x, y=y)

def drag_release(event, frame, grid_info):
    frame.lower()
    x, y = gui.gui_frame_layer.winfo_pointerxy()
    target_frame = gui.gui_frame_layer.winfo_containing(x, y).master
    # changeOrder(target_frame, frame, grid_info)

    # if isinstance(target_widget, ttk.Button):
    if target_frame.master is frame.master :
        changeOrder(target_frame, frame, grid_info)
        print(target_frame.grid_info())
    else:
        frame.grid(row=grid_info['row'], column=grid_info['column'])
