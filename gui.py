import main
import utils
import font_utils
import gui_utils as g
import gui_drag_drop

# import inspect
# import pprint
from PIL import ImageTk, Image
from fontTools.ttLib import TTFont
from fontTools.ttLib.ttGlyphSet import _TTGlyphGlyf
import tkinter as tk
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from tkinterdnd2 import DND_FILES
from functools import partial

def global_Interface(root):
    root.title('Alt-Font')
    ws, hs = root.winfo_screenwidth(), root.winfo_screenheight()
    wm, hm = ws/10, hs/10
    root.geometry('%dx%d+%d+%d' % (ws-wm, hs-hm, ws/2-(ws-wm)/2, hs/2-(hs-hm)/2))
    root.geometry('%dx%d+%d+%d' % (ws-350, hs, 0, 0))
    # if ws < 2000 : root.geometry("{0}x{1}+0+0".format(ws,hs))
    # if ws < 1500 : root.attributes("-fullscreen", True)
    print(ws)
    root.resizable()
    root.iconphoto(False, ImageTk.PhotoImage(Image.open(utils.path('files/logo.png'))))
    # root.tk.call('tk', 'scaling', 1.5)
    root.tk.call("source", utils.path("files/azure.tcl")) # theme
    root.tk.call("set_theme", "light")
    root.drop_target_register(DND_FILES) # drag & drop
    root.dnd_bind('<<Drop>>', lambda e: drop(root, e) )
    # root.option_add('*tearOff', 0)
    main.plugins, main.names = utils.load_plugins() # has to be loaded here
    menubar = Menu(root)
    root.config(menu=menubar)
    menu_items = dict.fromkeys( [ 'File', 'Help', 'New layer' ] )
    for key, val in menu_items.items():
        menu_items[key] = Menu(menubar)
        menubar.add_cascade( label=key, menu=menu_items[key] )

    menu_items['File'].add_command(label='New')
    menu_items['File'].add_command(label='Open...')
    menu_items['File'].add_command(label='Export', command=main.modify_font )
    menu_items['File'].add_separator()
    menu_items['File'].add_command( label='Exit', command=root.destroy )
    menu_items['Help'].add_command(label='Welcome')
    menu_items['Help'].add_command(label='About...')
    menu_items['New layer'].add_command( label='New group', command=main.new_group )
    menu_items['New layer'].add_separator()
    for i in range(len(main.plugins)) :
        menu_items['New layer'].add_command( label=main.names[i], command=partial(main.new_layer,i) )
    # layout on the root window
    # root.columnconfigure(0, weight=1) # ????????
    # root.columnconfigure(1, weight=2)

    global gui_frame_layer
    gui_frame_layer = ttk.Frame(root, style='Card.TFrame')
    gui_frame_layer.grid(column=0, row=0, columnspan=3, sticky='swne')
    root.bind("<Button-1>",gui_drag_drop.on_click)

    global gui_frame_param
    gui_frame_param = ttk.Frame(root, style='Card.TFrame')
    gui_frame_param.grid(column=0, row=1, columnspan=1, sticky='swne')
    main.new_group()

    frame = ttk.Frame(root, style='Card.TFrame')
    g.Slider(frame, max=1.34, name='potrace_curves', format='%0.2f').grid(column=1, row=3, sticky=tk.W)
    g.Slider(frame, max=1.5, name='potrace_simplify', format='%0.2f').grid(column=1, row=4, sticky=tk.W)
    g.Slider(frame, max=100, name='potrace_min' ).grid(column=1, row=5, sticky=tk.W)
    g.Slider(frame, max=2, name='potrace_size', format='%0.2f' ).grid(column=1, row=6, sticky=tk.W)
    # Slider(frame, 20, 0, 100, 40, 'name1', '%0.2f', flag='eco').grid(column=1, row=1, sticky=tk.W)
    g.Checkbutton(frame, name='potrace_simple').grid(column=0, row=1, sticky=tk.W)
    g.Checkbutton(frame, name='test_bool').grid(column=0, row=3, sticky=tk.W)
    global check_display_points
    check_display_points = g.Checkbutton(frame, name='display_points')
    check_display_points.grid(column=0, row=2, sticky=tk.W)

    for widget in frame.winfo_children():
        widget.grid(padx=5, pady=5)

    frame.grid(column=0, row=1, sticky='s')

    frame = ttk.LabelFrame(root, style='Card.TFrame', text='Global Info')
    frame.grid(column=3, row=0, sticky='swne')
    # frame.columnconfigure(0, weight=0)
    global gui_font_info
    gui_font_info = {'name':tk.StringVar(), 'numG':tk.StringVar() }
    ttk.Label(frame, textvariable=gui_font_info['name'] ).grid(column=0, row=0)
    ttk.Label(frame, textvariable=gui_font_info['numG'] ).grid(column=1, row=0)

    ttk.Button(frame, text='Replace').grid(column=0, row=1)
    ttk.Button(frame, text='Replace All').grid(column=0, row=2)
    ttk.Entry(frame, width=30).grid(column=0, row=3)
    for widget in frame.winfo_children(): widget.grid(padx=5, pady=5)

    # general key control
    root.bind("<Escape>", lambda x: production_esc(root))
    root.bind("<Right>", lambda x: show_glyph('next'))
    root.bind("<Left>", lambda x: show_glyph('prev'))
    root.bind("<KeyPress-space>", lambda e: print() if e.keysym=='Space' else check_display_points.update(1) )
    root.bind("<KeyRelease-space>", lambda e: print() if e.keysym=='Space' else check_display_points.update(0) )

    img = ImageTk.PhotoImage(main.img)
    global img_letter
    img_letter = Label(root, image=img)
    img_letter.grid(row=1, column=2,sticky=tk.NS, rowspan=2)


    img = ImageTk.PhotoImage( main.img.resize((10,10),1) )
    global btn_save_editor
    btn_save_editor = ttk.Button(root, text='Replace', compound=tk.LEFT)
    btn_save_editor.grid(row=0, column=0,rowspan=2)

    # self.facebookButton = ttk.Button(self.mainFrame, text='Facebook', image=self.facebookIcon, compound=LEFT)

def production_esc(root):
    root.destroy()
    main.modify_font()
def refresh():
    img = main.get_current_img()

    img = ImageTk.PhotoImage(img.crop((150, 150, img.width-150, img.height-150)).resize((int(img.width/2),int(img.height/2)),1) )
    global img_letter
    img_letter.configure( image=img )
    img_letter.image = img


def show_glyph(flag=''):
    glyph_set = main.font.getGlyphSet()
    if flag=='prev': main.current_glyph = utils.prev_key(glyph_set, main.current_glyph)
    if flag=='next': main.current_glyph = utils.next_key(glyph_set, main.current_glyph)
    # print('---', main.current_glyph, end=' - ')

    if 'CFF ' in main.font : print('Table : CFF ')
    if 'CFF2' in main.font : print('Table : CFF2')
    if 'glyf' in main.font :
        g = main.font['glyf'][main.current_glyph]
        # print('Table : glyf - has contour : ', g.numberOfContours)
        if g.isComposite():
            print(main.current_glyph, 'is composite')
        elif g.numberOfContours > 0:
            refresh()
        else :
            print('glyph has no contour', g.numberOfContours)
            show_glyph(flag)
    else :
        if main.current_glyph in glyph_set :
            refresh()
        else :
            print('show glyph error', flag, main.current_glyph)


def drop(root,e):
    load_new_font(e.data)
def load_new_font(data, refresh=False):
    if data[0] == '{': data = data[1:-1]
    main.font = TTFont( utils.path(data), recalcBBoxes=False )
    if 'glyf' in main.font :
        main.font = TTFont( utils.path(data), recalcBBoxes=True )
    # main.tmp_font = TTFont( utils.path(data), recalcBBoxes=False )
    gui_font_info['name'].set( str(main.font['name'].getName(1, 3, 1)) )
    gui_font_info['numG'].set( str(main.font['maxp'].numGlyphs) )
    print( f'LOAD FONT : (refresh={refresh}) {utils.path(data)}' )
    if refresh : refresh()


if __name__ == "__main__":
    print('RUN FROM GUI')
    main.main()
