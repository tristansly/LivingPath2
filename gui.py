import main, utils, font_utils, gui_drag_drop, save_data, wiki
import gui_utils as gu
from PIL import ImageTk, Image
from fontTools.ttLib import TTFont
from fontTools import unicodedata
import tkinter as tk
from tkinter import TclError, ttk, Tk, Frame, Menu, Label, filedialog
from tkinterdnd2 import DND_FILES
from functools import partial
from iso639 import language  # iso639 and not python-iso639
import uharfbuzz as hb
from hyperglot import checker, SupportLevel, parse, LanguageValidity
import pprint

def global_Interface(root):
    main.plugins, main.names = utils.load_plugins() # has to be loaded here
    setup_root(root)
    setup_menubar()

    global gui_zone, gui_para, gui_glob, notebook
    s = ttk.Style()
    s.configure('red.TFrame', background='red')
    s.configure('none.TButton', foreground="#ccc")
    frm_style = 'Card.TFrame'
    frm_style = ''
    gui_foot = ttk.Frame(root, style=frm_style)
    gui_info = ttk.Frame(gui_foot, style=frm_style)
    gui_zone = ttk.Frame(root, style=frm_style)
    ctn_para = ttk.Frame(root, style=frm_style)
    gui_glob = ttk.Frame(ctn_para, style=frm_style)
    gui_view = ttk.Frame(root, style=frm_style)


    ttk.Sizegrip(gui_foot).pack(side='right', anchor='se',  expand=False, padx=(0, 5), pady=(0, 5))
    gui_foot.pack(side='bottom', fill='x', expand=True, anchor='s', pady=(20,0))
    gui_info.pack(side='left', fill='x', expand=False, anchor='s')
    gui_zone.pack(side='top', fill='both', expand=True, anchor='n', pady=(10,20))
    ctn_para.pack(side='left', fill='y', expand=False, anchor='sw', padx=0, pady=0)
    gui_glob.pack(side='bottom', fill=None, expand=False, anchor='sw', padx=(20,0), pady=(20,0))
    gui_view.pack(side='left', fill='both', expand=True, anchor='w')

    gui_zone.bind_all("<Button-1>",gui_drag_drop.on_click)

    gu.Checkbutton(gui_glob, name='display_paths', ini=False).pack(anchor='w', pady=(20,0))
    global b_rules
    b_rules = gu.Checkbutton(gui_glob, name='display_rules', ini=False)
    b_rules.pack(anchor='w', pady=(0,20))
    s_space = gu.Slider(gui_glob, min=-150, max=250, name='letter_spacing', flag=None, ini=0 )
    s_space.callback = b_rules.select
    s_space.pack(anchor='w', pady=(0,20))

    vecto = ttk.LabelFrame(gui_glob, text="vectorization", padding=(10, 10))
    vecto.pack(anchor='w', padx=(0,0))
    gu.Slider(vecto, max=1.34, name='curves_limit', format='%0.2f', ini=0.90).pack(anchor='w')
    gu.Slider(vecto, max=1.5, name='simplify_path', format='%0.2f', ini=0.45).pack(anchor='w')
    # gu.Slider(vecto, max=500, name='min' , ini=2).pack(anchor='w')
    gu.Slider(vecto, min=0.01, max=2, name='accuracy', format='%0.2f' , ini=1).pack(anchor='w')

    gui_para = gu.ScrolledFrame(ctn_para, side='left' )
    gui_para.pack(side='top', fill='y', expand=True, anchor='n' )

    global gui_font_info
    gui_font_info = {'name':tk.StringVar(), 'numG':tk.StringVar(), 'unit':tk.StringVar() }
    ttk.Label(gui_info, textvariable=gui_font_info['name'] ).grid(column=0, row=0)
    ttk.Label(gui_info, textvariable=gui_font_info['numG'] ).grid(column=1, row=0)
    ttk.Label(gui_info, textvariable=gui_font_info['unit'] ).grid(column=2, row=0)
    for widget in gui_info.winfo_children(): widget.grid(padx=20, pady=(5,10))

    refresh_button = ttk.Button(gui_view, text="Refresh font", width=1.2)
    refresh_butto2 = ttk.Button(gui_view, text="↺", width=1.2)
    refresh_button.pack(side="top", anchor="ne")
    refresh_butto2.pack(side="right", anchor="ne")
    refresh_button.config( command = refresh_txt )
    refresh_butto2.config( command = new_wiki )

    global frame_txt
    frame_txt = gu.ScrolledFrame(gui_view, side='right')
    frame_txt.pack(side='right', fill='both', expand=True,  anchor='e' )

    global img_letter
    img = ImageTk.PhotoImage(main.img)
    img_letter = Label(gui_view, image=img)
    img_letter.pack(ipadx=0, ipady=0, side="left", fill='both', expand=False)
    img_letter.bind('<MouseWheel>', gu.scroll_letter)
    img_letter.bind('<Button-1>', lambda x: show_glyph("next") )
    img_letter.bind('<Button-3>', lambda x: show_glyph("prev") )
    # img_letter.config(cursor="sb_h_double_arrow")

    global img_txt
    img_txt = []
    for i in range(4):
        img_txt.append( Label(frame_txt.content, image=ImageTk.PhotoImage(main.img)) )
        img_txt[i].pack( ipadx=0, ipady=0,  fill='x', expand=True)

    gu.used_glyphs = []
    main.new_group()
    # main.new_layer(0) # test


def refresh(compute=True):
    img = main.get_current_img(main.current_glyph, compute=compute)
    m = 0 # font_utils.imgMargin
    img = img.crop((m, m, img.width-m, img.height-m)).resize((img.width//2,img.height//2),1)
    refresh_img(img_letter, img)

def refresh_txt():
    root.config(cursor="watch");
    root.update_idletasks()
    main.time(None)
    main.text_to_font(wiki.title, main.tmp_font, title="Process title")
    main.time("process title")

    print('\n',frame_txt.container.winfo_width(),
            frame_txt.canvas.winfo_width(),
            frame_txt.content.winfo_width(),
            frame_txt.yscrollbar.winfo_width())

    ctn_width = frame_txt.container.winfo_width()-30
    refresh_img(img_txt[0], text_titre(wiki.title, ctn_width, 150))
    frame_txt.updateContent()
    main.time("display title")

    # il n'y à rien dans wiki.start ...
    # main.text_to_font(wiki.start, main.tmp_font, title="Process subtitle" )
    # refresh_img(img_txt[1], text_block(wiki.start, 85, frame_txt.container.winfo_width() ))

    main.text_to_font(wiki.sum, main.tmp_font, title="Process text" )

    refresh_img(img_txt[1], text_block(wiki.sum, 55, ctn_width ))
    refresh_img(img_txt[2], text_block_double(wiki.sum, 45, ctn_width ))
    main.text_to_font("Agf", main.tmp_font, title="Process text" )
    refresh_img(img_txt[3], text_titre("Agf", ctn_width, 350))

    main.time("all texts")
    root.config(cursor="")
    gu.used_glyphs.clear()

def refresh_img(label, img):
    img = ImageTk.PhotoImage(img)
    label.configure( image = img )
    label.image = img
    label.update()

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
    # print('---', main.current_glyph, end=' - ')

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
    if hasattr(root,'config') : root.config(cursor="watch") ; root.update()

    if data[0] == '{': data = data[1:-1]
    main.font = TTFont( utils.path(data), recalcBBoxes=True ) # recalcBBoxes=False
    main.font_origin = TTFont( utils.path(data), recalcBBoxes=True ) # recalcBBoxes=False
    main.tmp_font = TTFont( utils.path(data), recalcBBoxes=True )
    if 'glyf' in main.font :
        main.font = TTFont( utils.path(data), recalcBBoxes=False )
        main.font_origin = TTFont( utils.path(data), recalcBBoxes=False ) # recalcBBoxes=False
        main.tmp_font = TTFont( utils.path(data), recalcBBoxes=False )
        print("[glyf] ", end=" ")
    else :
        print("[CFF] ", end=" ")

        # print('---', [k for k, v in main.font['CFF '].cff[0].rawDict.items()] )
        # print('---', [k+v for k, v in main.font['CFF '].cff[0].Private.rawDict.items()] )
        # print('---', main.font['CFF '].cff[0].Private.nominalWidthX )
        # print('---', main.font['CFF '].cff[0].FullName)
    print('--- u per em : ', main.font['head'].unitsPerEm) # TODO bigger fonts

    main.hbfont = hb.Font( hb.Face( hb.Blob.from_file_path(utils.path(data)) ) ) # load metric with uharfbuzz

    main.font_name = str(main.font['name'].getName(16, 3, 1))
    if main.font_name == 'None' : main.font_name = str(main.font['name'].getName(1, 3, 1))
    main.font_style = str(main.font['name'].getName(17, 3, 1))
    if main.font_style == 'None' : main.font_style = str(main.font['name'].getName(2, 3, 1))

    gui_font_info['name'].set( "Loaded font :  " + main.font_name + " - " + main.font_style )
    gui_font_info['numG'].set( "  " + str(main.font['maxp'].numGlyphs) + " glyphs" )
    gui_font_info['unit'].set( " resolution " + str(main.font['head'].unitsPerEm) + " units" )
    try:
        refresh()
    except: # if droped font has no main.current_glyph
        show_glyph('next')
    # refresh_txt()
    print("NEW FONT LOADED")

    # check = checker.FontChecker(utils.path(data))
    # typo = check.get_supported_languages(decomposed=False, supportlevel=SupportLevel.BASE.value )
    # for k,v in typo.items() : print("typo got : ", len(v), k)

    typo = {}
    # checkGlyph = checker.CharsetChecker( parse.parse_font_chars(main.font) )
    # typo = checkGlyph.get_supported_languages(decomposed=True,supportlevel=SupportLevel.BASE.value, validity=LanguageValidity.DRAFT.value)
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
    print("wiki",len(wiki.langs), end=' / ')
    print("combo",len(combo))
    menu_items['Language'].delete(0, "end") # populate menu/language
    for lang in combo :
        menu_items['Language'].add_command( label=lang[1], command=partial(set_lang, lang[0]) )

    if hasattr(root,'config') : root.config(cursor="")


def new_wiki():
    root.config(cursor="watch"); root.update_idletasks()
    wiki.get_wiki(); root.config(cursor="")
    refresh_txt()
def set_lang(lang):
    root.config(cursor="watch"); root.update_idletasks()
    wiki.set_wiki_lang(lang); root.config(cursor="")
    refresh_txt()

def production_esc(root):
    root.destroy()

#----------------------------------------------------------------------------------
def setup_menubar():
    menubar = Menu(root)
    root.config(menu=menubar)
    global menu_items
    menu_items = dict.fromkeys( [ 'File', 'Help', 'New layer', 'New group', 'Language' ] )
    for key, val in menu_items.items():
        menu_items[key] = Menu(menubar)
        menubar.add_cascade( label=key, menu=menu_items[key] )

    menu_items['File'].add_command( label='Import font',  command=import_font )
    menu_items['File'].add_command( label='Export font',  command=export_font )
    menu_items['File'].add_separator()
    menu_items['File'].add_command( label='Save project', command=save_data.dump)
    menu_items['File'].add_command( label='Open project', command=save_data.load )
    menu_items['Help'].add_command( label='Welcome')
    menu_items['Help'].add_command( label='About...')
    for i in range(len(main.plugins)) :
        menu_items['New layer'].add_command( label=main.names[i], command=partial(main.new_layer,i) )
    menu_items['New layer'].add_separator()
    menu_items['New layer'].add_command( label='Duplicate layer', command=main.duplicate_layer )
    menu_items['New group'].add_command( label='New group',       command=main.new_group )
    menu_items['New group'].add_separator()
    menu_items['New group'].add_command( label='Duplicate group', command=main.duplicate_group )
#----------------------------------------------------------------------------------
gs_flags = ('all','lowercase','uppercase','digits','punctuation')
def export_font(): # gui ask family name and style
    result = {'Font family name': main.font_name,'Font style': main.font_style,
    'combo:Glyph set': gs_flags}
    gu.AskBox(root, 'Name your font', result, selectFile_export)

def selectFile_export(data): # gui select folder to save font
    file_path = filedialog.asksaveasfilename(  title='Export Font File',
        initialdir=utils.path,
        defaultextension=".otf",
        filetypes=( ('Open Type Format','*.otf'), ('True Type Font','*.ttf'), ('All files','*.*') ),
        confirmoverwrite=True,
        initialfile = data['Font family name'].replace(' ', '_') + "-" + data['Font style']
    )
    with open(file_path,'wb') as f:
        root.config(cursor="watch");
        main.process_font_export(file_path, name=data['Font family name'], style=data['Font style'], flag=data['combo:Glyph set'])
        root.config(cursor="")

def import_font():
    filename = filedialog.askopenfilename(  title='Open Font file',
        initialdir=utils.path,
        defaultextension=('.otf','.ttf'),
        filetypes=( ('Font files',('*.otf','*.ttf')), ('All files','*.*') )
    )
    load_new_font(filename)
#----------------------------------------------------------------------------------

def setup_root(mainRoot):
    global root
    root = mainRoot
    # utils.check_time(root)
    root.title('LivingPath')
    root.overrideredirect(0)
    #root.overrideredirect(0)
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
                                        'children': [('Checkbutton.label', {'sticky': 'nswe'})]})]})]
             )
    style.configure('cover.TFrame', background="grey93")
    # root.option_add('*tearOff', 0)

    # layout on the root window
    root.columnconfigure(0, weight=2) # ????????
    root.columnconfigure(1, weight=2)

    # general key control
    root.bind("<Escape>", lambda x: production_esc(root))
    root.bind("<Right>", lambda x: show_glyph('next'))
    root.bind("<Left>", lambda x: show_glyph('prev'))
    root.bind('<Return>', lambda x: refresh_txt() )
    root.bind("<Control-e>", lambda x: export_font() ) # (MAC OS) replace Control by Meta
    root.bind("<Control-n>", lambda x: import_font() )
    root.bind("<Control-s>", lambda x: save_data.dump() )
    root.bind("<Control-o>", lambda x: save_data.load() )

#----------------------------------------------------------------------------------




if __name__ == "__main__":
    print('RUN FROM GUI')
    main.main()
