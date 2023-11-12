import gui_utils as gui
from base_plugin import Plugin

from PIL import ImageFilter

class Layer(Plugin):
    """Apply a blur then a threshold."""

    def __init__(s):
        super(Layer, s).__init__()

        s.blur_val = 40
        s.threshold_val = 90

    def gui(s, frame):
        gui.Slider(frame, max=200, layer=s, name='blur_val').grid(column=0, row=1, sticky='ew')
        gui.Slider(frame, max=200, layer=s, name='threshold_val').grid(column=0, row=2, sticky='ew')

    def run(s, img):
        img = img.filter( ImageFilter.GaussianBlur(radius = s.blur_val) )
        img = img.point( lambda p: 255 if p > s.threshold_val else 0 ) # threshold 128
        return img
