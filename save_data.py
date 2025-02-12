import pickle
from tkinter import filedialog as fd
import main, font_utils, gui, utils, gui_utils
import os.path

#------------------------------------------------------------------------------------------#
def writeParamFile(data, line = -1):
    try:
        if line != -1:
            params = readParamFile()
            params[line] = data
        else:
            params = data

        with open( utils.path('files/global_params.txt'), 'wb') as f:
            # print ('---write',params)
            pickle.dump(params, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        save_data.writeParamFile(['en','files/1.otf']) # init parameters.txt

def readParamFile(line = -1):
    try:
        with open( utils.path('files/global_params.txt'), 'rb') as f:
            data = pickle.load(f)
            # print('---read',data[line])
            if line != -1: return data[line]
            else:          return data
    except Exception as e:
        writeParamFile(['en','files/1.otf']) # init parameters.txt
#------------------------------------------------------------------------------------------#
def dump():
    filename = fd.asksaveasfilename(  title='Save LivingPath file',
    initialdir=utils.path,
    defaultextension=".lvp",
    filetypes=( ('LivingPath files','*.lvp'), ('All files','*.*') ),
    confirmoverwrite=True,
    initialfile = 'LivingPath parameters'
    )
    dumpFile(filename)

def dumpFile(filename):
    with open(filename,'wb') as f:

        data = []
        for g in main.groups :
            data_group = {}
            data_group['layers'] = []
            data_group['op'] = g.op
            data_group['n'] = g.n

            for l in g.layers:
                print("save layer", g.n, " - ", l.n)
                data_layer = {}
                data_layer['n'] = l.n
                data_layer['ref_plugin'] = l.ref_plugin
                data_layer['params'] = utils.get_layer_attr(l)
                data_group['layers'].append( data_layer )

            data.append( data_group )
        params = utils.get_layer_attr(font_utils.params)
        fontPath = main.font.reader.file.name

        pickle.dump( {'groups':data,'params':params,'font file': fontPath}, f, pickle.HIGHEST_PROTOCOL)


#------------------------------------------------------------------------------------------#

def load():
    filename = fd.askopenfilename(  title='Open LivingPath file',
        initialdir=utils.path,
        defaultextension=".lvp",
        filetypes=( ('LivingPath files','*.lvp'), ('All files','*.*') )
    )
    load_data(filename)

def load_data(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        for g in main.groups[::-1] : # delete all groups[reversed]
            if g is main.groups[0] :
                for n in range(len(g.layers)-1, -1, -1) : g.del_layer( n, refresh=False)
            else :
                main.del_group(g, select_last=False)
            print('------------- delete group : ',g.n)
        main.select_layer(main.groups[0].layers[0]) # bugfix (if not g0 selected)

        for name, val in data['params'] : # load global params
            setattr(font_utils.params, name, val)

        for data_group in data['groups'] : # build loaded groups
            if data_group['n'] != 0 : main.new_group()
            print("BUILD GROUP", data_group['n'])
            g = main.groups[-1]
            for name, val in data_group['layers'][0]['params'] : # set contour layer params
                setattr(g.layers[0], name, val)

            for data_layer in data_group['layers'][1:] : # build layers
                main.new_layer(data_layer['ref_plugin'], refresh=False)

                l = g.layers[-1]
                for name, val in data_layer['params'] : # set layer params
                    setattr(l, name, val)
                l.gui( gui.gui_para.content )

                l.change_order( g.n, data_layer['n'], refresh=False) # set layer position

            g.set_op(data_group['op'], refresh=False ) # set group op

        main.select_layer(main.groups[-1].layers[-1])
        if utils.path_name(data['font file']) != utils.path_name(main.font.reader.file.name) :
            try:
                if os.path.isfile(data['font file']):
                    gui.load_new_font(data['font file'])
            except:
                pass
                # result = { "label:" : data['font file']+"\n is missing" }
                # gui_utils.AskBox(main.root, "Unrecognised font", result,  btn1='ok')

        gui.refresh()
        print('NOMBRE DE GROUPES :', len(main.groups))
