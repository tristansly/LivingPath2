import main
import utils
import font_utils
import gui_utils as gu
import gui_drag_drop
from PIL import ImageTk, Image
from fontTools.ttLib import TTFont
from fontTools.ttLib.ttGlyphSet import _TTGlyphGlyf
import tkinter as tk
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from tkinterdnd2 import DND_FILES
from functools import partial

def global_Interface(root):
    main.plugins, main.names = utils.load_plugins() # has to be loaded here
    setup_root(root)
    setup_menubar(root)

    global gui_zone
    global gui_para
    global notebook
    frm_style = 'Card.TFrame'
    frm_style = ''
    gui_zone = ttk.Frame(root, style=frm_style)
    ctn_para = ttk.Frame(root, style=frm_style)
    gui_para = ttk.Frame(ctn_para, style=frm_style)
    gui_glob = ttk.Frame(ctn_para, style=frm_style)
    gui_info = ttk.Frame(root, style=frm_style)
    notebook = ttk.Notebook(root)

    ttk.Sizegrip(root).pack(side='bottom', anchor='se',  expand=False, padx=(0, 5), pady=(0, 5))
    gui_zone.pack(side='top', fill='x', expand=True)
    ctn_para.pack(side='left', fill='both', expand=False, padx=20, pady=20)
    gui_para.pack(side='top', fill='both', expand=False)
    gui_glob.pack(side='bottom', fill=None, expand=False,  anchor='sw')
    gui_info.pack(side='right', fill=None, expand=False)
    notebook.pack(side='left', fill='both', expand=True)

    # gui_zone.grid(column=0, row=0, columnspan=3, sticky='swne')
    # gui_para.grid(column=0, row=1, columnspan=1, sticky='nw', padx=20, pady=20 )
    # gui_glob.grid(column=0, row=2, sticky='s')
    # gui_info.grid(column=3, row=0, sticky='swne')
    # notebook.grid(row=1, column=2, sticky='nw', rowspan=2, columnspan=1)

    notebook.columnconfigure(0, weight=1)
    notebook.rowconfigure(0, weight=1)

    gui_zone.bind_all("<Button-1>",gui_drag_drop.on_click)

    gu.Slider(gui_glob, max=1.34, name='potrace_curves', format='%0.2f', ini=0.90).pack(anchor='w')
    gu.Slider(gui_glob, max=1.5, name='potrace_simplify', format='%0.2f', ini=0.45).pack(anchor='w')
    gu.Slider(gui_glob, max=500, name='potrace_min' , ini=2).pack(anchor='w')
    gu.Slider(gui_glob, max=2, name='potrace_size', format='%0.2f' , ini=1).pack(anchor='w')
    gu.Slider(gui_glob, min=-300, max=300, name='letter_spacing', flag='eco', ini=0).pack(anchor='w')
    gu.Checkbutton(gui_glob, name='potrace_simple', ini=True).pack(anchor='w')
    global check_display_points
    check_display_points = gu.Checkbutton(gui_glob, name='display_points', ini=False)
    check_display_points.pack(anchor='w')

    # for widget in gui_glob.winfo_children(): widget.grid(padx=0, pady=0, sticky='w')

    global gui_font_info
    gui_font_info = {'name':tk.StringVar(), 'numG':tk.StringVar() }
    ttk.Label(gui_info, textvariable=gui_font_info['name'] ).grid(column=0, row=0)
    ttk.Label(gui_info, textvariable=gui_font_info['numG'] ).grid(column=1, row=0)
    ttk.Entry(gui_info, width=30).grid(column=0, row=3)
    for widget in gui_info.winfo_children(): widget.grid(padx=5, pady=5)


    notebook.enable_traversal()
    notebook.bind('<<NotebookTabChanged>>', focus_current_tab)
    global tab_2
    tab_1 = ttk.Frame(notebook)
    for index in [0, 1]:
        tab_1.columnconfigure(index=index, weight=1)
        tab_1.rowconfigure(index=index, weight=1)
    notebook.add(tab_1, text="Tab 1")
    tab_2 = ttk.Frame(notebook)
    notebook.add(tab_2, text="Tab 2")

    global img_letter
    img = ImageTk.PhotoImage(main.img)
    img_letter = Label(tab_1, image=img, background='grey')
    img_letter.pack(ipadx=20, ipady=20, fill='both', expand=True)
    global img_txt
    img = ImageTk.PhotoImage(main.img)
    img_txt = Label(tab_2, image=img, background='white')
    img_txt.pack(ipadx=20, ipady=20,  side="left", expand=False)

    # general key control
    root.bind("<Escape>", lambda x: production_esc(root))
    root.bind("<Right>", lambda x: show_glyph('next'))
    root.bind("<Left>", lambda x: show_glyph('prev'))
    root.bind("<KeyPress-space>", lambda e: print() if e.keysym=='Space' else check_display_points.update(1) )
    root.bind("<KeyRelease-space>", lambda e: print() if e.keysym=='Space' else check_display_points.update(0) )

    main.new_group()
    main.new_layer(0) # test

def focus_current_tab(e):
    e.widget.winfo_children()[e.widget.index(e.widget.select())].focus_set()
    refresh()

def production_esc(root):
    root.destroy()

def refresh():
    if notebook.index(notebook.select())==0 : img = main.get_current_img(main.current_glyph)
    if notebook.index(notebook.select())==1 : img = main.text_to_img("VAwert")
    m = 0 # font_utils.imgMargin
    img = img.crop((m, m, img.width-m, img.height-m)).resize((int(img.width/2),int(img.height/2)),1)
    refresh_img(img_txt, img)
    refresh_img(img_letter, img)

def refresh_img(label, img):
    img = ImageTk.PhotoImage(img)
    label.configure( image = img )
    label.image = img


def show_glyph(flag=''):
    glyph_set = main.font.getGlyphSet()
    if flag=='prev': main.current_glyph = utils.prev_key(glyph_set, main.current_glyph)
    if flag=='next': main.current_glyph = utils.next_key(glyph_set, main.current_glyph)
    print('---', main.current_glyph, end=' - ')

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
    refresh()
def load_new_font(data):
    if data[0] == '{': data = data[1:-1]
    main.font = TTFont( utils.path(data), recalcBBoxes=False ) # recalcBBoxes=False
    main.font_origin = TTFont( utils.path(data), recalcBBoxes=False ) # recalcBBoxes=False
    main.tmp_font = TTFont( utils.path(data), recalcBBoxes=False )
    if 'glyf' in main.font :
        main.font = TTFont( utils.path(data), recalcBBoxes=True )
        main.font_origin = TTFont( utils.path(data), recalcBBoxes=True ) # recalcBBoxes=False
        main.tmp_font = TTFont( utils.path(data), recalcBBoxes=True )
    else :
        print("[CFF] ", end=" ")

    import uharfbuzz as hb
    main.hbfont = hb.Font( hb.Face( hb.Blob.from_file_path(utils.path(data)) ) ) # load metric with uharfbuzz
    gui_font_info['name'].set( str(main.font['name'].getName(1, 3, 1)) )
    gui_font_info['numG'].set( str(main.font['maxp'].numGlyphs) )
    print("NEW FONT LOADED")

#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
def setup_menubar(root):
    menubar = Menu(root)
    root.config(menu=menubar)
    menu_items = dict.fromkeys( [ 'File', 'Help', 'New layer' ] )
    for key, val in menu_items.items():
        menu_items[key] = Menu(menubar)
        menubar.add_cascade( label=key, menu=menu_items[key] )

    menubar.add_command( label='New group', command=main.new_group )

    menu_items['File'].add_command(label='New')
    menu_items['File'].add_command(label='Open...')
    menu_items['File'].add_command(label='Export', command=main.modify_font )
    menu_items['File'].add_separator()
    menu_items['File'].add_command( label='Exit', command=root.destroy )
    menu_items['Help'].add_command(label='Welcome')
    menu_items['Help'].add_command(label='About...')
    for i in range(len(main.plugins)) :
        menu_items['New layer'].add_command( label=main.names[i], command=partial(main.new_layer,i) )
    menu_items['New layer'].add_separator()

#----------------------------------------------------------------------------------
def setup_root(root):
    root.title('Alt-Font')
    ws, hs = root.winfo_screenwidth(), root.winfo_screenheight()
    wm, hm = ws/10, hs/10
    root.geometry('%dx%d+%d+%d' % (ws-wm, hs-hm, ws/2-(ws-wm)/2, hs/2-(hs-hm)/2))
    root.geometry('%dx%d+%d+%d' % (ws-550, hs-300, 0, 0)) #production
    # if ws < 2000 : root.geometry("{0}x{1}+0+0".format(ws,hs))
    # if ws < 1500 : root.attributes("-fullscreen", True)
    # root['background'] = 'white' # for linux distro ?
    root.iconphoto(False, ImageTk.PhotoImage(Image.open(utils.path('files/logo.png'))))
    # root.tk.call('tk', 'scaling', 1.5)
    root.tk.call("source", utils.path("files/azure.tcl")) # theme
    root.tk.call("set_theme", "light")
    root.drop_target_register(DND_FILES) # drag & drop
    root.resizable()
    root.dnd_bind('<<Drop>>', lambda e: drop(root, e) )
    style = ttk.Style()
    style.layout('no_indicatoron.TCheckbutton', # pathfinders buttons
             [('Checkbutton.padding', {'sticky': 'nswe', 'children': [
                 # ('Checkbutton.indicator', {'side': 'left', 'sticky': ''}),
                 ('Checkbutton.focus', {'side': 'left', 'sticky': 'w',
                                        'children':
                                        [('Checkbutton.label', {'sticky': 'nswe'})]})]})]
             )
    style.configure('cover.TFrame', background="grey93")
    # root.option_add('*tearOff', 0)

    # layout on the root window
    root.columnconfigure(0, weight=2) # ????????
    root.columnconfigure(1, weight=2)
#----------------------------------------------------------------------------------






if __name__ == "__main__":
    print('RUN FROM GUI')
    main.main()
