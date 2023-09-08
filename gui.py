import main
import utils
import font_utils
import gui_utils as g

import inspect
import pprint
from PIL import ImageTk, Image
from fontTools.ttLib import TTFont
from fontTools.ttLib.ttGlyphSet import _TTGlyphGlyf
import tkinter as tk
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from tkinterdnd2 import DND_FILES

def global_Interface(root):
    root.title('Alt-Font')
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    root.geometry('%dx%d+%d+%d' % (ws-400, hs-150, ws/2-(ws-400)/2, hs/2-(hs-150)/2))
    root.resizable()
    root.iconphoto(False, ImageTk.PhotoImage(Image.open(utils.path('files/logo.png'))))
    # root.tk.call('tk', 'scaling', 1.5)
    root.bind("<Escape>", lambda x: root.destroy()) # general key control
    root.bind("<Right>", lambda x: show_glyph('next'))
    root.bind("<Left>", lambda x: show_glyph('prev'))
    # frame.bind("<KeyRelease>", keyup)
    root.tk.call("source", utils.path("files/ttk-theme/azure.tcl")) # theme
    root.tk.call("set_theme", "dark")
    root.drop_target_register(DND_FILES) # drag & drop
    root.dnd_bind('<<Drop>>', lambda e: drop(root, e) )
    # create a menubar
    menubar = Menu(root)
    root.config(menu=menubar)

    file_menu = Menu( menubar, tearoff=0 )
    file_menu.add_command(label='New')
    file_menu.add_command(label='Open...')
    file_menu.add_command(label='Close')
    file_menu.add_separator()
    file_menu.add_command( label='Exit', command=root.destroy )
    menubar.add_cascade( label="File", menu=file_menu )

    help_menu = Menu( menubar, tearoff=0 )
    help_menu.add_command(label='Welcome')
    help_menu.add_command(label='About...')
    menubar.add_cascade( label="Help", menu=help_menu )

    # layout on the root window
    # root.columnconfigure(0, weight=0) # ????????
    # root.columnconfigure(1, weight=2)
    input_frame = create_input_frame(root)
    input_frame.grid(column=0, row=0)

    button_frame = create_button_frame(root)
    button_frame.grid(column=1, row=0)

    img = ImageTk.PhotoImage(main.img)
    global img_letter
    img_letter = Label(root, image=img)
    img_letter.grid(row=0, column=3)
def refresh():
    img = ImageTk.PhotoImage( main.get_current_img() )
    global img_letter
    img_letter.configure( image=img )
    img_letter.image = img

def show_glyph(flag=''):

    glyph_set = main.font.getGlyphSet()
    if flag=='prev': main.current_glyph = utils.prev_key(glyph_set, main.current_glyph)
    if flag=='next': main.current_glyph = utils.next_key(glyph_set, main.current_glyph)
    print('---', main.current_glyph, end=' - ')

    if 'CFF ' in main.font : print('Table : CFF ')
    if 'CFF2' in main.font : print('Table : CFF2')
    if 'glyf' in main.font :
        g = main.font['glyf'][main.current_glyph]
        print('Table : glyf - has contour : ', g.numberOfContours)
        if g.isComposite():
            print(main.current_glyph, 'is composite')
        elif g.numberOfContours > 0:
            refresh()
        else :
            print('glyph has no contour', g.numberOfContours)
            show_glyph(flag)
    else :
        if main.current_glyph in glyph_set :
            print('uknown font')
            refresh()
        else :
            print('show glyph error', flag, main.current_glyph)


def drop(root,e):
    load_new_font(e.data)
def load_new_font(data):
    if data[0] == '{': data = data[1:-1]
    global font
    del main.font # ?
    del main.tmp_font
    main.font     = TTFont( utils.path(data), recalcBBoxes=False )
    main.tmp_font = TTFont( utils.path(data), recalcBBoxes=False )
    print( utils.path(data) )
    refresh()

def create_input_frame(container):

    frame = ttk.Frame(container)

    # grid layout for the input frame
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(0, weight=3)

    ############################### fontTool
    font = TTFont(utils.path("files/citizen.ttf"))
    # font['name'] gets the name table,
    # getName gets a specified name ID (1), platform (3 for Windows), and platEncID (1)
    name1 = str(font['name'].getName(1, 3, 1))
    # help(font['name']) # use help() for more methods on a given table

    ttk.Label(frame, text=name1).grid(column=0, row=0, sticky=tk.W)
    keyword = ttk.Entry(frame, width=30)
    keyword.grid(column=1, row=0, sticky=tk.W)

    ttk.Label(frame, text = main.names[main.current_plugin]).grid(column=0, row=1, sticky=tk.W)
    main.modules[main.current_plugin].gui(frame)



    g.Slider(frame, max=1.34, ini=0.90, name='potrace_curves', format='%0.2f').grid(column=1, row=3, sticky=tk.W)
    g.Slider(frame, max=1.5, ini=0.15, name='potrace_simplify', format='%0.2f').grid(column=1, row=4, sticky=tk.W)
    g.Slider(frame, max=100, ini=2, name='potrace_min' ).grid(column=1, row=5, sticky=tk.W)
    g.Slider(frame, max=2, ini=1, name='potrace_size', format='%0.2f' ).grid(column=1, row=6, sticky=tk.W)
    # Slider(frame, 20, 0, 100, 40, 'name1', '%0.2f', flag='eco').grid(column=1, row=1, sticky=tk.W)
    g.Checkbutton(frame, ini=1, name='potrace_simple').grid(column=0, row=2, sticky=tk.W)
    g.Checkbutton(frame, ini=1, name='test_bool').grid(column=0, row=3, sticky=tk.W)
    global check_display_points
    check_display_points = g.Checkbutton(frame, ini=0, name='display_points')
    check_display_points.grid(column=0, row=4, sticky=tk.W)
    container.bind("<KeyPress-space>", lambda e: print() if e.keysym=='Space' else check_display_points.update(1) )
    container.bind("<KeyRelease-space>", lambda e: print() if e.keysym=='Space' else check_display_points.update(0) )

    for widget in frame.winfo_children():
        widget.grid(padx=5, pady=5)

    return frame


def create_button_frame(container):
    frame = ttk.Frame(container)
    frame.columnconfigure(0, weight=1)
    ttk.Button(frame, text='Find Next').grid(column=0, row=0)
    ttk.Button(frame, text='Replace').grid(column=0, row=1)
    ttk.Button(frame, text='Replace All').grid(column=0, row=2)
    for widget in frame.winfo_children():
        widget.grid(padx=5, pady=5)
    return frame




if __name__ == "__main__":
    print('RUN FROM GUI')
    main.main()
