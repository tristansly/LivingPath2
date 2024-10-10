import pickle
from tkinter import filedialog as fd
import main, font_utils, gui, utils


#------------------------------------------------------------------------------------------#
def dump():
    filename = fd.asksaveasfilename(  title='Save LivingPath file',
        initialdir=utils.path,
        defaultextension=".lvp",
        filetypes=( ('LivingPath files','*.lvp'), ('All files','*.*') ),
        confirmoverwrite=True,
        initialfile = 'LivingPath parameters'
    )
    with open(filename,'wb') as f:

        data = []
        for g in main.groups :
            data_group = {}
            data_group['layers'] = []
            data_group['op'] = g.op

            for l in g.layers:
                print("save layer", g.n, " - ", l.n)
                data_layer = {}
                data_layer['n'] = l.n
                data_layer['ref_plugin'] = l.ref_plugin
                data_layer['params'] = utils.get_layer_attr(l)
                data_group['layers'].append( data_layer )

            data.append( data_group )
        params = utils.get_layer_attr(font_utils.params)

        pickle.dump( {'groups':data,'params':params}, f, pickle.HIGHEST_PROTOCOL)


#------------------------------------------------------------------------------------------#

def load():
    filename = fd.askopenfilename(  title='Open LivingPath file',
        initialdir=utils.path,
        defaultextension=".lvp",
        filetypes=( ('LivingPath files','*.lvp'), ('All files','*.*') )
    )

    with open(filename, 'rb') as f:
        data = pickle.load(f)
        for g in main.groups[::-1] : # delete all groups
            for n in range(len(g.layers)-1, -1, -1) :
                g.del_layer( n, refresh=False)
            print('------------- delete group : ',g.n)
            main.del_group(g.n, select_last=False)

        for name, val in data['params'] : # load global params
            setattr(font_utils.params, name, val)

        for data_group in data['groups'] : # build loaded groups
            main.new_group()
            g = main.groups[-1]
            for name, val in data_group['layers'][0]['params'] : # set group contour layer params
                setattr(g.layers[0], name, val)

            for data_layer in data_group['layers'][1:] : # build layers
                main.new_layer(data_layer['ref_plugin'], refresh=False)

                l = g.layers[-1]
                for name, val in data_layer['params'] : # set layer params
                    setattr(l, name, val)
                l.gui( gui.gui_para )

                l.change_order( g.n, data_layer['n'], refresh=False) # set layer position

            g.set_op(data_group['op'], refresh=False ) # set group op

        main.select_layer(main.groups[-1].layers[-1])
        gui.refresh()
        print('nombre de groupes :', len(main.groups))
