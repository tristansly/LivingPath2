import main
import utils
import font_utils
import gui_utils as gu
import gui_drag_drop
import save_data
import wiki
from PIL import ImageTk, Image
from fontTools.ttLib import TTFont
from fontTools.ttLib.ttGlyphSet import _TTGlyphGlyf
from fontTools import unicodedata
import tkinter as tk
from tkinter import TclError, ttk, Tk, Frame, Menu, Label
from tkinterdnd2 import DND_FILES
from functools import partial
import pickle
from iso639 import language  # iso639 and not python-iso639
import uharfbuzz as hb
from hyperglot import checker, SupportLevel, parse, LanguageValidity
import pprint

def global_Interface(root):
    main.plugins, main.names = utils.load_plugins() # has to be loaded here
    setup_root(root)
    setup_menubar(root)

    global gui_zone
    global gui_para
    global gui_glob
    global notebook
    frm_style = 'Card.TFrame'
    frm_style = ''
    gui_zone = ttk.Frame(root, style=frm_style)
    ctn_para = ttk.Frame(root, style=frm_style)
    gui_para = ttk.Frame(ctn_para, style=frm_style)
    gui_glob = ttk.Frame(ctn_para, style=frm_style)
    gui_view = ttk.Frame(root, style=frm_style)
    gui_foot = ttk.Frame(root, style=frm_style)
    gui_info = ttk.Frame(gui_foot, style=frm_style)

    ttk.Sizegrip(gui_foot).pack(side='right', anchor='se',  expand=False, padx=(0, 5), pady=(0, 5))
    gui_foot.pack(side='bottom', fill='x', expand=True,  anchor='s')
    gui_info.pack(side='left', fill='x', expand=False,  anchor='s')
    gui_zone.pack(side='top', fill='x', expand=True)
    ctn_para.pack(side='left', fill='both', expand=False, padx=20, pady=20)
    gui_para.pack(side='top', fill='both', expand=False)
    gui_glob.pack(side='bottom', fill=None, expand=False,  anchor='sw')
    gui_view.pack(side='left', fill='both', expand=True, anchor='w')

    # gui_zone.grid(column=0, row=0, columnspan=3, sticky='swne')
    # gui_para.grid(column=0, row=1, columnspan=1, sticky='nw', padx=20, pady=20 )
    # gui_glob.grid(column=0, row=2, sticky='s')
    # gui_info.grid(column=3, row=0, sticky='swne')
    # notebook.grid(row=1, column=2, sticky='nw', rowspan=2, columnspan=1)

    gui_zone.bind_all("<Button-1>",gui_drag_drop.on_click)

    gu.Slider(gui_glob, min=-150, max=250, name='letter_spacing', flag='eco', ini=0).pack(anchor='w')
    gu.Checkbutton(gui_glob, name='display_points', ini=False, slow=False).pack(anchor='w', pady=(20,0))
    gu.Checkbutton(gui_glob, name='display_rules', ini=False, slow=False).pack(anchor='w', pady=(0,20))
    gu.Slider(gui_glob, max=1.34, name='potrace_curves', format='%0.2f', ini=0.90).pack(anchor='w')
    gu.Slider(gui_glob, max=1.5, name='potrace_simplify', format='%0.2f', ini=0.45).pack(anchor='w')
    gu.Slider(gui_glob, max=500, name='potrace_min' , ini=2).pack(anchor='w')
    gu.Slider(gui_glob, max=2, name='potrace_size', format='%0.2f' , ini=1).pack(anchor='w')

    # for widget in gui_glob.winfo_children(): widget.grid(padx=0, pady=0, sticky='w')

    global gui_font_info
    gui_font_info = {'name':tk.StringVar(), 'numG':tk.StringVar() }
    ttk.Label(gui_info, textvariable=gui_font_info['name'] ).grid(column=0, row=0)
    ttk.Label(gui_info, textvariable=gui_font_info['numG'] ).grid(column=1, row=0)
    for widget in gui_info.winfo_children(): widget.grid(padx=20, pady=(5,10))

    refresh_button = ttk.Button(gui_view, text="Refresh font", width=1.2)
    refresh_butto2 = ttk.Button(gui_view, text="↺", width=1.2)
    refresh_button.pack(side="top", anchor="ne")
    refresh_butto2.pack(side="right", anchor="ne")
    refresh_button.config( command = refresh_txt )
    refresh_butto2.config( command = new_wiki )

    global canvas
    canvas = tk.Canvas(gui_view, borderwidth=0)
    frame_txt = tk.Frame(canvas)
    vsb = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="right", fill="both", expand=True)
    canvas.create_window((0,0), window=frame_txt, anchor="nw")
    frame_txt.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    set_mousewheel(frame_txt, lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units") ) # not linux proof

    global img_letter
    img = ImageTk.PhotoImage(main.img)
    img_letter = Label(gui_view, image=img)
    img_letter.pack(ipadx=0, ipady=0, side="left", fill='both', expand=False)
    global img_txt
    img_txt = []
    for i in range(4):
        img_txt.append( Label(frame_txt, image=ImageTk.PhotoImage(main.img)) )
        img_txt[i].pack(ipadx=0, ipady=0,  fill='x', expand=True)

    # general key control
    root.bind("<Escape>", lambda x: production_esc(root))
    root.bind("<Right>", lambda x: show_glyph('next'))
    root.bind("<Left>", lambda x: show_glyph('prev'))
    root.bind("<KeyPress-space>", lambda e: print() if e.keysym=='Space' else check_display_points.update(1) )
    root.bind("<KeyRelease-space>", lambda e: print() if e.keysym=='Space' else check_display_points.update(0) )

    gu.used_glyphs = []
    main.new_group()
    main.new_layer(0) # test

def set_mousewheel(widget, command): # Activate/deactivate mousewheel scrolling when cursor is over the widget
    widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', command))
    widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))

def onFrameConfigure(canvas): # Reset the scroll region to encompass the inner frame
    canvas.configure(scrollregion=canvas.bbox("all"))

def refresh():
    img = main.get_current_img(main.current_glyph)
    m = 0 # font_utils.imgMargin
    img = img.crop((m, m, img.width-m, img.height-m)).resize((img.width//2,img.height//2),1)
    refresh_img(img_letter, img)

def refresh_txt():
    root.config(cursor="watch");
    root.update()
    main.time(None)
    main.text_to_font(wiki.title, main.tmp_font)
    main.time("process title")

    refresh_img(img_txt[0], text_titre(wiki.title, canvas.winfo_width(), 150))
    main.time("display title")

    main.text_to_font(wiki.start, main.tmp_font )
    refresh_img(img_txt[1], text_block(wiki.start, 85, canvas.winfo_width() ))

    main.text_to_font(wiki.sum, main.tmp_font )
    refresh_img(img_txt[2], text_block(wiki.sum, 45, canvas.winfo_width() ))
    refresh_img(img_txt[3], text_block_double(wiki.sum, 45, canvas.winfo_width() ))

    main.time("all texts")
    root.config(cursor="")

def refresh_img(label, img):
    img = ImageTk.PhotoImage(img)
    label.configure( image = img )
    label.image = img
    label.update()
    gu.used_glyphs.clear()

def text_line(txt, w, h, dir='rl'):
    img = main.text_to_img_HB(txt, main.tmp_font, main.hbfont)
    img.thumbnail((w,h), Image.Resampling.LANCZOS)
    return img

def text_titre(txt, w, h, dir='rl'):
    bg = Image.new('L', (w, 3000), (255))
    stack, y = '', 0
    for word in utils.cutWords(txt):
        if len(stack) < 7 :
            stack += word
        else:
            bg.paste( text_line(stack,w*2,h,dir='rl'), (0,y) )
            y +=h
            stack = word
    if stack != '' : bg.paste( text_line(stack,w*2,h,dir='rl'), (0,y) )

    bg = bg.crop((0, 0, w, y+h ))
    return bg

def text_block(txt, txt_size, w, dir='rl' ):
    bg = Image.new('L', (w+500, 2000), (255))
    i, y, x, max, lh = 0, 40, 0, 0, 0
    for word in utils.cutWords(txt) :
        img = main.text_to_img_HB(word, main.tmp_font, main.hbfont)
        img.thumbnail((3000, txt_size), Image.Resampling.LANCZOS)
        lh = img.height
        if x+img.width > bg.width :
            y += lh # interlignage
            if max < x : max = x # line width max
            x = 0
            if y > bg.height-lh : break
        bg.paste(img, (x, y) )
        x += img.width
    bg = bg.crop((0, 0, max, y+lh ))
    bg.thumbnail((w, 2000), Image.Resampling.LANCZOS)
    return bg

def text_block_double(txt, txt_size, w, dir='rl'):
    words = txt.split(' ')
    txt1 = ' '.join( words[0:len(words)//2] )
    txt2 = ' '.join( words[len(words)//2:] )
    bg = Image.new('L', (w, 3000), (255))
    img = text_block(txt1, txt_size, w//2-20, dir='rl' )
    im2 = text_block(txt2, txt_size, w//2-20, dir='rl' )
    bg.paste(img, (0,0) )
    bg.paste(im2, (img.width+40,0) )
    bg = bg.crop((0, 0, w, max(img.height,im2.height) ))
    return bg

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
            show_glyph('next' if flag=='' else flag)
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
def load_new_font(data):
    if hasattr(main.root,'config') : main.root.config(cursor="watch") ; main.root.update()

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

    main.hbfont = hb.Font( hb.Face( hb.Blob.from_file_path(utils.path(data)) ) ) # load metric with uharfbuzz

    gui_font_info['name'].set( "Loaded font :  " + str(main.font['name'].getName(1, 3, 1)) )
    gui_font_info['numG'].set( "  " + str(main.font['maxp'].numGlyphs) + " glyphs" )
    try:
        refresh()
    except: # if droped font has no main.current_glyph
        show_glyph('next')
    # refresh_txt()
    print("NEW FONT LOADED")

    # check = checker.FontChecker(utils.path(data))
    # typo = check.get_supported_languages(decomposed=False, supportlevel=SupportLevel.BASE.value )
    # for k,v in typo.items() : print("typo got : ", len(v), k)

    checkGlyph = checker.CharsetChecker( parse.parse_font_chars(main.font) )
    typo = checkGlyph.get_supported_languages(decomposed=True,supportlevel=SupportLevel.BASE.value, validity=LanguageValidity.DRAFT.value)
    for k,v in typo.items() : print("typo got : ", len(v), k)

    combo = []
    wikikeys = []
    for k in wiki.langs :
        # print( language.Language.match(k).part3, k)
        try:
            wikikeys.append( (k, language.Language.match(k).part3) )
        except Exception as e:
            print('iso639 != wikiLang : missing ', k)
        #     pass

    for wk in wikikeys :
        for v in typo.values():
            # print(wk[1])
            if wk[1] in v :
                combo.append( (wk[0], str(v[wk[1]])[8:], v[wk[1]]['speakers'] ) )
                break # skip same lang in differents categories

    combo = sorted(combo, key=lambda k:k[2], reverse=True ) # sort by lang speakers
    # for v in combo : print(v[1], v[2] )
    print("wiki",len(wiki.langs))
    print("combo",len(combo))
    menu_items['Language'].delete(0, "end") # populate menu/language
    for lang in combo :
        menu_items['Language'].add_command( label=lang[1], command=partial(set_lang, lang[0]) )

    if hasattr(root,'config') : root.config(cursor="")


def new_wiki():
    root.config(cursor="watch"); root.update()
    wiki.get_wiki(); root.config(cursor="")
    refresh_txt()
def set_lang(lang):
    root.config(cursor="watch"); root.update()
    wiki.set_wiki_lang(lang); root.config(cursor="")
    refresh_txt()

def production_esc(root):
    root.destroy()

#----------------------------------------------------------------------------------
def setup_menubar(root):
    menubar = Menu(root)
    root.config(menu=menubar)
    global menu_items
    menu_items = dict.fromkeys( [ 'File', 'Help', 'New layer', 'New group', 'Language' ] )
    for key, val in menu_items.items():
        menu_items[key] = Menu(menubar)
        menubar.add_cascade( label=key, menu=menu_items[key] )

    menu_items['File'].add_command(label='New')
    menu_items['File'].add_command(label='Save project', command=save_data.dump)
    menu_items['File'].add_command(label='Open project', command=save_data.load )
    menu_items['File'].add_command(label='Export font', command=main.modify_font )
    menu_items['File'].add_separator()
    menu_items['File'].add_command( label='Exit', command=root.destroy )
    menu_items['Help'].add_command(label='Welcome')
    menu_items['Help'].add_command(label='About...')
    for i in range(len(main.plugins)) :
        menu_items['New layer'].add_command( label=main.names[i], command=partial(main.new_layer,i) )
    menu_items['New layer'].add_separator()
    menu_items['New layer'].add_command( label='Duplicate layer', command=partial(main.duplicate_layer) )
    menu_items['New group'].add_command( label='New group', command=main.new_group )
    menu_items['New group'].add_separator()
    menu_items['New group'].add_command( label='Duplicate group', command=partial(main.duplicate_group) )
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

def setup_root(mainRoot):
    global root
    root = mainRoot
    root.title('Alt-Font')
    ws, hs = root.winfo_screenwidth(), root.winfo_screenheight()
    wm, hm = ws/10, hs/10
    root.geometry('%dx%d+%d+%d' % (ws-wm, hs-hm, ws/2-(ws-wm)/2, hs/2-(hs-hm)/2))
    root.geometry('%dx%d+%d+%d' % (ws-550, hs-100, 0, 0)) #production
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


    with open(utils.path("files\lorem.txt")) as file:
        global lorem_ipsum
        lorem_ipsum = file.readlines()
        lorem_ipsum = [item.rstrip() for item in lorem_ipsum] # delete line jump
#----------------------------------------------------------------------------------




if __name__ == "__main__":
    print('RUN FROM GUI')
    main.main()
