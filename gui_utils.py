from utils import *
import font_utils, gui
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import TclError, ttk, Tk, Frame, Menu, Label, Entry
import inspect
from functools import partial

class Slider(ttk.Frame):
    def __init__(s, context, size=200, min=0,max=100, layer=None, name='', format="%d", flag='', ini=0, slow=False, callback=None):
        super(Slider, s).__init__(context)
        s.callback = callback
        s.format = format
        s.name = name.replace(' ', '_')
        s.flag = flag
        s.layer = font_utils.params if layer == None else layer
        if not hasattr(s.layer, s.name) : s.set_attach_val(ini) # set ini only at layer init

        s.val = ttk.Label(s, text = s.format % s.get_attach_val()) # display fix slider number
        s.val.grid(column=1, row=1, sticky=tk.W, padx=5 )
        s.slider_var = tk.DoubleVar()
        s.slider = ttk.Scale(s, from_=min, to_=max, length=size,
            orient='horizontal', style='Tick.TScale', variable=s.slider_var )
        s.slider.set( s.get_attach_val() )
        s.slider.configure(command = s.update)
        # s.slider.bind('<ButtonRelease-1>', s.update_eco)
        s.slider.grid(column=0, row=1, sticky=tk.W)

        s.title = ttk.Label(s, text = name.replace('_',' ') if not slow else name.replace('_', ' ')+'  ⏳' )
        s.title.grid(column=0, row=0, sticky=tk.W)

    def update(s, event):
        s.val.configure(text=s.get())
        if ( s.flag!='eco' ) and getattr( s.layer, s.name )!= None :
        # if ( s.flag!='eco' and not font_utils.display_points ) and getattr( s.layer, s.name )!= None :
            s.set_attach_val()
            if s.callback : s.callback()
            gui.show_glyph()

    def update_eco(s, event):
        if ( s.flag=='eco' ) and getattr( s.layer, s.name )!= None :
        # if ( s.flag=='eco' or font_utils.display_points ) and getattr( s.layer, s.name )!= None :
            s.set_attach_val()
            if s.callback : s.callback()
            gui.show_glyph()

    def set_attach_val(s, val=None ):
        if val==None : val = s.get() # if not ini
        if s.format == '%d' : setattr(s.layer, s.name, int(val))
        if s.format != '%d' : setattr(s.layer, s.name, float(val))
    def get_attach_val(s):
        return getattr(s.layer, s.name)
    def get(s):
        return s.format % float( s.slider.get() )
    def switch(s): switch(s)

class LockSliders(ttk.Frame):
    def __init__(s, context, ini, slider1, slider2):
        super(LockSliders, s).__init__(context)
        s.s1, s.s2 = Slider(s,**slider1), Slider(s,**slider2)
        s.s1.grid(row=0, column=0, sticky='w')
        s.s2.grid(row=1, column=0, sticky='w')
        s.layer = s.s1.layer
        s.name = s.s1.name+s.s2.name
        s.ico_on = get_img('lock-on.png', (20,50))
        s.ico_off = get_img('lock-off.png', (20,50))
        s.b = ttk.Checkbutton( s, width=1.2, style='no_indicatoron.TCheckbutton',
                command=s.toggle, compound="left", takefocus=False)
        gui.root.update()
        s.b.grid(row=0, column=1, rowspan=3, sticky='s', pady=(0,3))
        if hasattr(s.layer, s.name) : s.lock = not getattr( s.layer, s.name )
        else : s.lock = not ini # set ini only at layer init
        s.toggle()
    def toggle(s):
        s.lock = not s.lock
        if s.lock: s.b['image'], s.s1.callback, s.s2.callback = s.ico_on, s.set_s2, s.set_s1
        else:      s.b['image'], s.s1.callback, s.s2.callback = s.ico_off, None, None
        if s.lock and s.s2.get() != s.s1.get() :
            s.set_s2()
            gui.show_glyph()
        setattr(s.layer, s.name, s.lock)
    def set_s1(s):
        s.s1.slider_var.set( s.s2.get() ) # update slider without trigger command
        s.s1.val.configure(text=s.s2.get()) # update label
        s.s1.set_attach_val() # update attached layer val
    def set_s2(s):
        s.s2.slider_var.set( s.s1.get() ) # update slider without trigger command
        s.s2.val.configure(text=s.s1.get()) # update label
        s.s2.set_attach_val() # update attached layer val
    def switch(s, flag=None): switch(s.s1,s.s2,s.b, flag=flag)


class Checkbutton(ttk.Frame):
    def __init__(s, context, layer=None, name='', ini=False, slow=False, callback=None):
        super(Checkbutton, s).__init__(context)
        s.callback = callback
        s.name = name.replace(' ', '_')
        s.layer = font_utils.params if layer == None else layer
        s.var = tk.StringVar()
        if not hasattr(s.layer, s.name) : s.set_attach_val(ini) # set ini only at layer init
        s.var.set( s.get_attach_val() )
        s.check = ttk.Checkbutton( s, text=name.replace('_',' ') if not slow else name.replace('_', ' ')+'  ⏳', variable=s.var )
        s.check.configure(command = s.update)
        s.check.grid(column=0, row=0, sticky=tk.W)

    def update(s, val='undefined'):
        if getattr( s.layer, s.name ) != None and val != int(s.var.get()):
            if val != 'undefined': s.var.set(val)
            s.set_attach_val()
            if s.callback : s.callback()
            gui.show_glyph()

    def set_attach_val(s, val=False):
        if not val : val = s.var.get()
        setattr(s.layer, s.name, int(val or 0))

    def get_attach_val(s):
        return getattr(s.layer, s.name)

    def select(s):
        if int(s.var.get()) == 0 : s.check.invoke()


#--------------------------------------------------------------------------------

class Optionbutton(ttk.Frame):
    def __init__(s, context, layer=None, nbr=0, ini=0, pos='inline', name='', img_name=None, callback=None):
        super(Optionbutton, s).__init__(context)
        s.layer = font_utils.params if layer == None else layer
        s.name = name.replace(' ', '_')
        if img_name : name = img_name
        s.label = ttk.Label(s, text = s.name+" : ")
        s.label.grid(column=0, row=0, sticky=tk.W, padx=0 )
        s.callback = callback
        s.ico_off, s.ico_on, s.b = [], [], []
        for i in range(nbr) :
            s.ico_on.append( get_img(name+'-on-'+str(i)+'.png', (20,20)) )
            s.ico_off.append( get_img(name+'-off-'+str(i)+'.png', (20,20)) )
            s.b.append( ttk.Checkbutton( s, width=1.2, style='no_indicatoron.TCheckbutton',
                command=partial(s.set,i), compound="left", takefocus=False ) )
            s.b[i].grid( row=0, column=i+1 )

        if hasattr(s.layer, s.name) : ini = getattr(s.layer, s.name) # set ini only at layer init
        s.set(ini, refresh=False)

    def set(s, i, refresh=True):
        s.var = i
        for i in range(len(s.b)) : s.b[i]['image'] = s.ico_on[i] if i==s.var else s.ico_off[i]
        setattr(s.layer, s.name, int(s.var or 0))
        if s.callback : s.callback()
        if refresh: gui.refresh()


#----------------------------------------------------------------------------------

def switch(*elems, flag=None):
    for gui_elem in elems:
        for child in gui_elem.winfo_children():
            if hasattr(child, 'state'):
                print("state",child["state"]) # idk why not working without this print...
                if flag==False: child.configure(state='disabled')
                if flag==True : child.configure(state='normal')
                if flag==None :
                    if child["state"] == "normal": child.configure(state='disabled')
                    else: child.configure(state='normal')
                    # child.state(["disabled"]) # not working (ttk)
#----------------------------------------------------------------------------------

class Separator(ttk.Separator):
    def __init__(s, context, layer=None ):
        super(Separator, s).__init__(context)

#----------------------------------------------------------------------------------
def get_img(name, size=None):
    img = Image.open(path('files/theme/'+name))
    if size: img = img.resize(size, Image.HAMMING)
    return ImageTk.PhotoImage(img)
#----------------------------------------------------------------------------------

class ScrolledFrame(): # https://github.com/nikospt/tk-ScrolledFrame/
    def __init__( self, parent, side='right', axis='y', *args, **kwargs):
        self.container = tk.Frame(parent)
        self.canvas = tk.Canvas( self.container, *args, **kwargs )
        self.content = tk.Frame(self.canvas)
        self.parent = parent
        self.side = side
        self.xscrollbar = None
        self.yscrollbar = None
        if axis == 'y' or axis == 'xy' or axis == 'yx' or axis == 'both':
            self.yscrollbar = ttk.Scrollbar( self.container, orient='vertical', command=self.canvas.yview)
        if axis == 'x' or axis == 'xy' or axis == 'yx' or axis == 'both':
            self.xscrollbar = ttk.Scrollbar( self.container, orient='horizontal', command=self.canvas.xview)
        self.root = parent.winfo_toplevel()
        self.canvas.create_window( (0,0), window=self.content, anchor='nw')
        # if self.yscrollbar != None: # Dont bind scroll wheel unless y is an axis of this scrollframe
        self.root.bind("<Configure>", self.resize)


    def updateContent(self):
        self.content.update()

        if self.yscrollbar != None :
            self.yscrollbar.pack( side=self.side,  fill='y', padx=(5,5) )
            # self.canvas.configure( yscrollcommand=self.yscrollbar.set, scrollregion="0 0 0 %s" % self.content.winfo_height() )
            self.canvas.configure( yscrollcommand=self.yscrollbar.set, scrollregion=self.canvas.bbox("all") )
            if self.canvas.yview() == (0.0, 1.0) : # content fit container
                if self.side=="left": self.yscrollbar.place(width=0, height=0) # hide
                [self.UnBindMouseWheel(x) for x in [self.content,self.canvas,self.container]]
            else :
                # self.yscrollbar.pack_forget()
                if self.side=="left": self.yscrollbar.place(anchor="nw", width=20, height=self.container.winfo_height()) # show
                [self.BindMouseWheel(x) for x in [self.content,self.canvas,self.container]]
                self.bindChildren( self.content)

        self.canvas.pack( side='top', fill='both', expand=True, padx=(20,0) if self.side=="left" else (0,0) )
        self.container.update()
        # self.resize()

    def BindMouseWheel(self,widget):
        if self.root.call('tk', 'windowingsystem') == 'x11':
            widget.bind('<Button-4>',self.scrolldown)
            widget.bind('<Button-5>',self.scrollup)
        else: widget.bind('<MouseWheel>',self.scrollMouseWheel)
    def UnBindMouseWheel(self,widget):
        if self.root.call('tk', 'windowingsystem') == 'x11':
            widget.unbind('<Button-4>')
            widget.unbind('<Button-5>')
        else: widget.unbind('<MouseWheel>')

    def scrollMouseWheel(self,event):
        self.canvas.yview_scroll(int(-1*event.delta/120), 'units') # not linux proof ?
    def scrolldown(self,event): self.canvas.yview_scroll(-4, 'units')
    def scrollup(self,event): self.canvas.yview_scroll(4, 'units')

    def bindChildren(self,widget):
        children = widget.winfo_children()
        if len(children) != 0:
            for child in enumerate(children):
                self.BindMouseWheel(child[1])
                self.bindChildren(child[1])

    def grid(self,*args, **kwargs): self.container.grid(*args,**kwargs)
    def pack(self,*args, **kwargs): self.container.pack(*args,**kwargs)

    def resize(self,*args):
        height = min( [self.content.winfo_height(), self.parent.winfo_height()-10 ] )
        self.canvas.configure( height=height, width=self.content.winfo_width() )
def scroll_letter(e):
    if e.delta > 0 : gui.show_glyph('prev')
    if e.delta < 0 : gui.show_glyph('next')

# def get_calling_module():
#     name = inspect.getmodule(inspect.stack()[2][0]).__name__.split('.')[-1]
#     print('get calling module', name)
#     return font_utils if name == 'gui' else get_plugin(name)

#----------------------------------------------------------------------------------

class AskBox(object):
    root = None
    def __init__(self, root, title, data=None, callback=None):
        """ data = <sequence> (dictionary, key) to associate with user input
        (providing a sequence for data creates an entry for user input) """
        self.root = root
        self.top = tk.Toplevel(self.root)
        self.top.iconphoto(False, ImageTk.PhotoImage(Image.open(path('files/logo.png'))))
        self.top.title(title)
        self.root.eval(f'tk::PlaceWindow {str(self.top)} center')
        self.callback = callback

        frame = ttk.Frame(self.top)
        frame.pack(fill='both', expand=True, padx=50, pady=50)

        self.entries = {}
        for key, val in data.items():
            if (key.startswith('combo:')):
                label = ttk.Label(frame, text=key[6:])
                label.pack(fill='x', expand=True, padx=0, pady=(20,0))
                self.entries[key] = ttk.Combobox(frame, values=val)
                self.entries[key].pack(fill='x', expand=True, pady=10)
                self.entries[key].current(0)
            else :
                label = ttk.Label(frame, text=key)
                label.pack(fill='x', expand=True, padx=0, pady=(20,0))
                self.entries[key] = ttk.Entry(frame)
                self.entries[key].pack(fill='x', expand=True, pady=10)
                self.entries[key].insert(0, val)

        b_submit = ttk.Button(frame, text='Export')
        b_submit['command'] = lambda: self.entry_to_dict(data)
        b_submit.pack(side='left', padx=0, pady=(20,0))

        b_cancel = ttk.Button(frame, text='Cancel')
        b_cancel['command'] = self.top.destroy
        b_cancel.pack(side='left', padx=(20,0), pady=(20,0))
        self.top.bind('<Return>', lambda event=None: b_submit.invoke() )
        self.top.bind('<Escape>', lambda event=None: b_cancel.invoke() )

    def entry_to_dict(self, data):
        for key, val in data.items():
            entry = self.entries[key].get()
            if entry:
                data[key] = entry
        self.top.destroy()
        self.callback(data)

class LoadBox(object):
    root = None
    def __init__(self, root, title):
        """ Loading bar """
        self.root = root
        self.top = tk.Toplevel(self.root)
        self.top.iconphoto(False, ImageTk.PhotoImage(Image.open(path('files/logo.png'))))
        self.top.title(title)
        self.root.eval(f'tk::PlaceWindow {str(self.top)} center')
        frame = ttk.Frame(self.top)
        frame.pack(fill='both', expand=True, padx=50, pady=30)

        self.txt = tk.StringVar()
        ttk.Label(frame, textvariable=self.txt).pack(fill='x', expand=True, padx=0, pady=(0,0))

        self.progress = ttk.Progressbar( frame, value=0, length=100, mode="determinate" )
        self.progress.pack(fill='x', expand=True, padx=0, pady=(20,0))

        self.stop = False
        b_cancel = ttk.Button(frame, text='Skip')
        b_cancel['command'] = self.cancel
        b_cancel.pack(side='bottom', padx=50, pady=(20,20))
        self.top.bind('<Escape>', lambda event=None: b_cancel.invoke() )

    def cancel(self):
        self.stop = True
