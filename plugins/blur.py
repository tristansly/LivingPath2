import gui_utils as gui
from base_plugin import Plugin
from PIL import ImageFilter, Image
import cv2
import numpy as np
from functools import partial
import math, utils

class Layer(Plugin):
    """Apply a noise."""

    def gui(s, frame):
        l = gui.LockSliders( frame, True,
            dict(max=200, ini=30, layer=s, name='blur_width'),
            dict(max=200, ini=30, layer=s, name='blur_height') )
        l.pack(sticky='nw')

        c = gui.Slider(frame, max=200, ini=150, layer=s, name='threshold_val'); c.pack(anchor='nw')

        gui.Checkbutton(frame, layer=s, ini=False, name='only_round_edges',
            callback=partial(gui.switch,c,l.s2) ).pack(anchor='nw')



    def run(s, img):
        if (not s.only_round_edges):
            img = img.filter( ImageFilter.GaussianBlur(radius = (s.blur_width,s.blur_height) ) )
            img = img.point( lambda p: 255 if p > s.threshold_val else 0 ) # threshold 128
        if (s.only_round_edges):
            img = cv2.medianBlur( np.asarray(img),
                utils.constrain(math.floor(s.blur_width), 0,145) *2+1  )

            img = Image.fromarray(img, mode='L')

        return img
