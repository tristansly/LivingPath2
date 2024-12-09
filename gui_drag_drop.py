
from tkinter import *
from functools import partial

from tkinter import Button, Label, Entry, Tk, SE, ttk
from PIL import ImageTk, Image
import main
import gui


def changeOrder(widget1, widget2, initial):
    print("start changeorder")
    for g in main.groups :
        for l in g.layers :
            if l.frame is widget2 :
                col = widget1.grid_info()['column'] //2
                row = widget1.grid_info()['row']
                if row is 0 : row += 1  # dont take "outline" layer position
                l.change_order( col , row )
                return None
    frame.grid(row=initial['row'], column=initial['column'])
    print('ALERT DRAG N DROP LOST')

def on_click(event):
    btn = event.widget
    # print('drag',btn)
    if isinstance(btn, ttk.Button) and btn['text'] == 'lll':
        frame = event.widget.master
        start = (event.x,event.y)
        grid_info = frame.grid_info()
        clone = clone_widget(frame, frame.master)
        clone.grid(row=frame.grid_info()['row'], column=frame.grid_info()['column'] )
        btn.bind("<B1-Motion>", lambda event:drag_motion(event, frame, start))
        btn.bind("<ButtonRelease-1>", lambda event:drag_release(event, frame, clone, grid_info))
        print('CLICK : frame ', frame)

    # j'ai cru que c'etait ça qui fait bugger les slider et en fait nan... est ce que ça sert à qqchose ce unbind ?
    else:
        gui.gui_zone.unbind("<ButtonRelease-1>")


def drag_motion(event, frame, start):
    x = frame.winfo_x()+event.x-start[0]
    y = frame.winfo_y()+event.y-start[1]
    frame.lift()
    frame.place(x=x, y=y)

def drag_release(event, frame, clone, grid_info):
    clone.destroy()
    frame.lower()
    x, y = gui.gui_zone.winfo_pointerxy()
    target = gui.gui_zone.winfo_containing(x, y)
    target_frame = target.master
    print('-RELEASE : frame ', frame)
    print('-RELEASE : target_frame ', target_frame)

    if target_frame.master is frame.master and target_frame is not frame : # target is not outline
        changeOrder(target_frame, frame, grid_info)
        print("SWAP LAYERS :", target_frame )
    else :
        print("SWAP ABORTED :", target_frame )
        frame.grid(row=grid_info['row'], column=grid_info['column'])

def on_enter(event):
    event.widget.configure( style='Card.TFrame' )
    print("--- enter---")
def on_leave(event):
    event.widget.configure( style='' )
    print("--- leave---")





def clone_widget(widget, master=None):
    """
    Create a cloned version o a widget

    Parameters
    ----------
    widget : tkinter widget
        tkinter widget that shall be cloned.
    master : tkinter widget, optional
        Master widget onto which cloned widget shall be placed. If None, same master of input widget will be used. The
        default is None.

    Returns
    -------
    cloned : tkinter widget
        Clone of input widget onto master widget.
    """
    # Get main info
    parent = master if master else widget.master
    cls = widget.__class__

    # Clone the widget configuration
    cfg = {key: widget.cget(key) for key in widget.configure()}
    cloned = cls(parent, **cfg)

    # copy widget position
    if widget.grid_info():
        grid_info = {k: v for k, v in widget.grid_info().items() if k not in {'in'}}
        cloned.grid(**grid_info)
    elif widget.place_info():
        place_info = {k: v for k, v in widget.place_info().items() if k not in {'in'}}
        cloned.place(**place_info)
    else:
        pack_info = {k: v for k, v in widget.pack_info().items() if k not in {'in'}}
        cloned.pack(**pack_info)

    # Clone the widget's children
    for child in widget.winfo_children():
        child_cloned = clone_widget(child, master=cloned)

    # grey cover
    if isinstance(cloned, ttk.Frame) : ttk.Frame(cloned, style='cover.TFrame').grid(row=0,column=0, rowspan=1,columnspan=3, sticky='nsew')

    return cloned
