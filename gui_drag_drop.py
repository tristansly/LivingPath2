
from tkinter import *
from functools import partial

from tkinter import Button, Label, Entry, Tk, SE, ttk
from PIL import ImageTk, Image
import main
import gui


def changeOrder(widget1, widget2, initial, last_elem=False):
    print("start changeorder")
    for g in main.groups :
        for l in g.layers :
            if l.frame is widget2 :
                col = widget1.grid_info()['column'] //2
                row = widget1.grid_info()['row']
                if row == 0 : row += 1  # dont take "outline" layer position
                if last_elem : row = len(main.groups[col].layers)
                l.change_order( col , row )
                return None
    frame.grid(row=initial['row'], column=initial['column'])
    print('ALERT DRAG N DROP LOST')

def on_click(event):
    btn = event.widget
    # print('drag',btn)
    if ( isinstance(btn, ttk.Button)
    and btn['text'] == 'lll'
    and not btn['style'] == 'transparent.TButton' ):
        frame = event.widget.master
        start = (event.x,event.y)
        grid_info = frame.grid_info()
        clone = clone_widget(frame, frame.master)
        clone.grid(row=frame.grid_info()['row'], column=frame.grid_info()['column'] )
        btn.bind("<B1-Motion>", lambda event:drag_motion(event, frame, start))
        btn.bind("<ButtonRelease-1>", lambda event:drag_release(event, frame, clone, grid_info))
        print('CLICK : frame ', frame)


def drag_motion(event, frame, start):
    x = frame.winfo_x()+event.x-start[0]
    y = frame.winfo_y()+event.y-start[1]

    current_frame = frame.place_info().get("in") # used to lift over differents frames
    frame.place( x=x, y=y)
    frame.lift()


def drag_release(event, frame, clone, grid_info):
    clone.destroy()
    frame.lower()
    event.widget.unbind("<ButtonRelease-1>")
    event.widget.unbind("<B1-Motion>")
    x, y = gui.gui_zone.winfo_pointerxy()
    target = gui.gui_zone.winfo_containing(x, y)
    itself = None

    if target : itself = target.master # to check if target == moved frame

    target_frame = None if not target else target.master


    last_elem = False # if target is outside try target column
    if ( not target_frame or target_frame.master is not frame.master or target_frame is frame ):
        print('not BUTTON')
        last_elem = True
        target = gui.gui_zone.winfo_containing(x, frame.master.winfo_rooty()+5)

    target_frame = None if not target else target.master

    print('frame', frame)
    print('target', gui.gui_zone.winfo_containing(x, y).master)

    if ( target_frame
    and target_frame.master is frame.master
    and target['style'] != 'cover.TFrame'
    and frame is not itself
    and target_frame is not frame ): # target is not outline
        changeOrder(target_frame, frame, grid_info, last_elem=last_elem)
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
    if isinstance(cloned, ttk.Frame) :
        ttk.Frame(cloned, style='cover.TFrame').grid(row=0,column=0, rowspan=1,columnspan=4, sticky='nsew')

    return cloned
